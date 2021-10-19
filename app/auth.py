import fastapi
import oso
import sqlalchemy
import app.db
import app.settings
import app.models

import sqlmodel as sql
import sqlalchemy_oso.session as sqloso
import app.models as m
import starlette.responses as responses

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Header, Request, Depends
from typing import Optional
from authlib.jose import jwt
from fastapi.security import OpenIdConnect

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

oauth2_scheme = OpenIdConnect(openIdConnectUrl=CONF_URL)

READ_ACTION = "read"
WRITE_ACTION = "write"

## Authorized DB Session
def make_oso_authorized_db(oso_instance: oso.Oso = None, 
                            action: str = READ_ACTION):
                            
    def get_authorized_db(request: fastapi.Request, 
                            engine: sqlalchemy.engine.Engine = fastapi.Depends(app.db.get_engine)):
        sessionmaker = sqloso.authorized_sessionmaker(get_oso = lambda: oso_instance, 
                                                        get_user = lambda: request.state.user,
                                                        get_checked_permissions = lambda: {  m.User: action,
                                                                                            m.Species: action}, 
                                                        bind=engine)
        with sessionmaker() as session:
            yield session
    
    return get_authorized_db


## JWT
_PRIVATE_PEM = conf("JWT_PRIVATE_PEM")
_PUBLIC_PEM = conf("JWT_PUBLIC_PEM")

## Authentication
def current_user(request: Request, 
                token: str = Depends(oauth2_scheme),
                session: app.db.Session = Depends(app.db.get_session)):
    try:
        claims = jwt.decode(token, _PUBLIC_PEM)
        claims.validate()
        
        email = claims["sub"]

        u = _get_or_create_user_by_email(session, email)

        request.state.user = m.SerializedUser(email=email, id=u.id)

        return request.state.user
    except Exception as e:
        raise HTTPException(403, str(e))


router = fastapi.APIRouter()

@router.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs
async def login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = request.url_for('auth')

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.api_route('/auth', methods=['GET', 'POST'], response_model=app.models.AuthToken)
async def auth(request: Request, session: app.db.Session = Depends(app.db.get_session)) -> app.models.AuthToken:
    # Perform Google OAuth
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)

    # Save the user
    user_email = dict(user).get('sub')
    user = _get_or_create_user_by_email(session, user_email)

    # Generate and return our JWT
    auth_token = _make_token(user.email)

    return app.models.AuthToken(token=auth_token, token_type="Bearer")


@router.get('/token', response_model=app.models.AuthToken, tags=['authentication'])
async def refresh(user: app.models.SerializedUser = Depends(current_user), session: app.db.Session = Depends(app.db.get_session)) -> app.models.AuthToken:
    auth_token = _make_token(user.email)

    return app.models.AuthToken(token=auth_token, token_type="Bearer")


_OAUTH_USER_SESSION_KEY = 'oauth-user'

@router.get('/logout', tags=['authentication'])  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop(_OAUTH_USER_SESSION_KEY, None)

    # TODO invalidate token

    return responses.RedirectResponse(url='/')


def _make_token(user_email):
    header = {'alg': 'RS256'}
    payload = {'iss': _issuer, 'aud': _audience, 'sub': user_email} #TODO iat

    auth_token = jwt.encode(header, payload, _PRIVATE_PEM)

    return auth_token


def _get_or_create_user_by_email(session: app.db.Session, email: str) -> m.User:
    user = session.query(m.User).filter(m.User.email == email).first()
    if user:
        return user
    return _create_user(session, m.UserBase(email=email))


def _create_user(session: app.db.Session, user: m.UserBase) -> m.SerializedUser:
    db_user = m.User(email=user.email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return m.SerializedUser(email=user.email, id=db_user.id)

