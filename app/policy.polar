# RBAC policy for Garden API
# https://docs.osohq.com/guides/rbac.html

resource Species {
    roles = ["owner"];
    permissions = ["read", "write", "delete"];

    "read" if "owner";
    "write" if "owner";
    "delete" if "owner";
}


actor User {}


has_role(user: User, "owner", species: Species) if
    species.owner = user;

# Allow Species creation
allow(_: User, "create", _: Species);

# Allow an action if the actor has permission "action" on the resource
allow(actor, action, resource) if
  has_permission(actor, action, resource);