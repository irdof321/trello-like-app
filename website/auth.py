from mozilla_django_oidc.auth import OIDCAuthenticationBackend

class MyOIDCAB(OIDCAuthenticationBackend):

    def create_user(self, claims):
        print("Cresting a new user")
        user = super().create_user(claims)        
        roles = claims.get("realm_access", {}).get("roles", [])
        user.is_staff = "django-staff" in roles
        user.is_superuser = "django-superuser" in roles
        print(f"{claims["preferred_username"]} is a superuser : {user.is_superuser}")
        user.save()
        return user
    
    def update_user(self, user, claims): 
        print("Updating a new user")     
        print("The claims ---------")
        print(claims)
        print("-------------------")  
        roles = claims.get("realm_access", {}).get("roles", [])
        print(f"Roles are {roles}")
        user.is_staff = "django-staff" in roles
        user.is_superuser = "django-superuser" in roles
        print(f"{claims["preferred_username"]} is a superuser : {user.is_superuser}")
        user.save()
        return user