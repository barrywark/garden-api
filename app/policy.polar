# RBAC policy for Garden API
# https://docs.osohq.com/guides/rbac.html

resource Garden {
    permissions = ["read", "write", "delete"];
    roles = ["owner", "contributor"];

    "read" if "contributor";
    "write" if "contributor";
    "delete" if "owner";

    "contributor" if "owner";
}

resource Zone {
    permissions = ["create", "read", "write", "delete"];
    roles = ["admin", "user"];

    "create" if "admin";
    "read" if "admin";
    "write" if "admin";
    "delete" if "admin";

    "read" if "user";
}


resource Species {
    roles = ["owner", "admin"];
    permissions = ["read", "write", "delete"];

    "read" if "admin";
    "write" if "admin";
    "delete" if "admin";

    "admin" if "owner";
}

resource Planting {
    roles = ["contributor"];
    permissions = ["read","write","delete"];

    "read" if "contributor";
    "write" if "contributor";
    "delete" if "contributor";

    relations = {garden: Garden};

    "contributor" if "contributor" on "garden";
}


actor User {}

#region Relations
has_relation(garden: Garden, "garden", planting: Planting) if
    planting.garden = garden;
#endregion


#region Roles
has_role(user: User, "owner", garden: Garden) if
    garden.owner = user;

has_role(user: User, "admin", _: Zone) if
    user.is_superuser;

has_role(_: User, "user", _: Zone);

has_role(user: User, "owner", species: Species) if
    species.owner = user;

#endregion

# Allow Species creation
allow(_: User, "create", _: Species);
allow(_: User, "create", _: Garden);

# Allow an action if the actor has permission "action" on the resource
allow(actor, action, resource) if
    has_permission(actor, action, resource);