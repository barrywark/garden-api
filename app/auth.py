import fastapi
import oso
import sqlalchemy
import app.db
import app.settings
import app.models

import sqlmodel as sql
import sqlalchemy_oso as sqloso
import app.models as m
import starlette.responses as responses

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Header, Request, Depends
from typing import Optional
from authlib.jose import jwt

conf = app.settings.get_env_config()
_issuer, _audience = conf("ISSUER"), conf("AUDIENCE")
_SCOPE = 'gardens'

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(conf)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


## Authorized DB Session
def make_get_authorized_db(oso: oso.Oso = None, engine: sqlalchemy.engine.Engine = app.db.ENGINE):
    def get_authorized_db(request: fastapi.Request):
        sessionmaker = sqloso.authorized_sessionmaker(lambda: oso, 
                                                    lambda: request.state.user,
                                                    lambda: request.scope["endpoint"].__name__, 
                                                    bind=engine)
        with sessionmaker() as session:
            yield session
    
    return get_authorized_db


## JWT
_PRIVATE_PEM = conf("JWT_PRIVATE_PEM")
_PUBLIC_PEM = conf("JWT_PUBLIC_PEM")

## Authentication
def _get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(403, "Missing 'Authorization' header.")
    try:
        return authorization.split()[1]
    except IndexError:
        raise HTTPException(403, "Malformed 'Authorization' header.")

        
def current_user(request: Request, 
                token: str = Depends(_get_token), 
                db: app.db.Session = Depends(app.db.get_session)):
    try:
        claims = jwt.decode(token, _PUBLIC_PEM)
        claims.validate()
        
        email = claims["sub"]

        request.state.user = _get_or_create_user_by_email(db, email) # TODO does `request.state` survive across requests?

        return request.state.user
    except Exception as e:
        raise HTTPException(403, str(e))


router = fastapi.APIRouter()

@router.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs
async def login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = request.url_for('auth')

    return await oauth.google.authorize_redirect(request, redirect_uri)


_OAUTH_USER_SESSION_KEY = 'oauth-user'
@router.api_route('/auth', methods=['GET', 'POST'], response_model=app.models.AuthToken)
async def auth(request: Request, db: app.db.Session = Depends(app.db.get_session)) -> app.models.AuthToken:
    # Perform Google OAuth
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)

    # Save the user
    user_email = dict(user).get('sub')
    user = _get_or_create_user_by_email(db, user_email)

    # Generate and return our JWT
    auth_token = _make_token(db, user.email)

    return app.models.AuthToken(token=auth_token)


@router.get('/token', response_model=app.models.AuthToken, tags=['authentication'])
async def refresh(user: app.models.User = Depends(current_user), db: app.db.Session = Depends(app.db.get_session)) -> app.models.AuthToken:
    user_email = dict(user).get('sub')
    auth_token = _make_token(db, user_email)

    return app.models.AuthToken(token=auth_token)


@router.get('/logout', tags=['authentication'])  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop(_OAUTH_USER_SESSION_KEY, None)

    # TODO invalidate token

    return responses.RedirectResponse(url='/')


def _make_token(db, user_email):
    header = {'alg': 'RS256'}
    payload = {'iss': _issuer, 'aud': _audience, 'sub': user.email} #TODO iat

    auth_token = jwt.encode(header, payload, _PRIVATE_PEM)

    return auth_token


def _get_or_create_user_by_email(db: app.db.Session, email: str) -> m.User:
    user = db.query(m.User).filter(m.User.email == email).first()
    if user:
        return user
    return _create_user(db, m.UserBase(email=email))


def _create_user(db: app.db.Session, user: m.UserBase) -> m.User:
    db_user = m.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

