from functools import wraps

import requests
from flask import request
from jose import jwt

AUTH0_DOMAIN = 'dev-wsb8jitr.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    """
    Obtains the access token from the authorization header
    :return: token
    """
    token = request.headers.get('Authorization')

    if not token:
        raise AuthError('no authorization header', 401)

    # analyse token parts
    token_parts = token.split()

    # should have 2 parts
    if len(token_parts) != 2:
        raise AuthError('authorization token should contain two parts', 401)

    bearer = token_parts[0]
    token = token_parts[1]

    # first part should be 'Bearer'
    if bearer.capitalize() != 'Bearer':
        raise AuthError('first part of the token should be Bearer', 401)

    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    pass
    # raise Exception('Not Implemented')


def verify_decode_jwt(token):
    jwks = requests.get('https://dev-wsb8jitr.auth0.com/.well-known/jwks.json')
    jwks = jwks.json()

    try:
        header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError('invalid token', 400)

    rsa_key = {}

    if 'kid' not in header:
        raise AuthError("'kid' not in header", 401)

    for key in jwks['keys']:
        if key['kid'] == header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=ALGORITHMS,
                        audience=API_AUDIENCE,
                        issuer='https://' + AUTH0_DOMAIN + '/'
                    )
                    return payload
                except jwt.ExpiredSignatureError:
                    raise AuthError('expired token', 401)
                except jwt.JWTClaimsError:
                    raise AuthError('invalid claims', 401)
                except Exception:
                    raise AuthError('invalid header', 400)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
