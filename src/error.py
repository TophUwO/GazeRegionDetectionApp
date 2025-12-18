from enum  import Enum
from quart import Response, jsonify


class ResponseStatus(Enum):
    Ok                  = 0
    InvalidSessionToken = 1
    SessionNotFound     = 2
    CannotSupplyImages  = 3
    InternalError       = 4
    InvalidStage        = 5
    MissingAuthToken    = 6
    InvalidAuthToken    = 7
    MissingSessionToken = 8
    MalformedRequest    = 9


def FormatResponse(type: ResponseStatus, payload: dict[str, any] | None = None) -> tuple[Response, int]:
    GL_ERRORDICT: dict[ResponseStatus, tuple[str, str, int]] = {
        ResponseStatus.Ok:                  ('ok',    'no error',                      200),
        ResponseStatus.InvalidSessionToken: ('error', 'Invalid session token.',        404),
        ResponseStatus.SessionNotFound:     ('error', 'Session not found.',            404),
        ResponseStatus.CannotSupplyImages:  ('error', 'Cannot supply images.',         403),
        ResponseStatus.InternalError:       ('error', 'Internal error occurred.',      500),
        ResponseStatus.InvalidStage:        ('error', 'Invalid stage ID.',             500),
        ResponseStatus.MissingAuthToken:    ('error', 'Missing authentication token.', 400),
        ResponseStatus.InvalidAuthToken:    ('error', 'Invalid authentication token.', 401),
        ResponseStatus.MissingSessionToken: ('error', 'Missing session token.',        400),
        ResponseStatus.MalformedRequest:    ('error', 'Malformed request.',            400)
    }
    
    try:
        cat, msg, code = GL_ERRORDICT[type]

        return jsonify(
            {
                "type":    cat,
                "desc":    msg,
                "code":    code,
                "payload": payload
            }
        ), code
    except KeyError:
        print(f'error: Invalid response status \'{cat}\'.')

    return FormatResponse(ResponseStatus.InternalError, { '__extra__': f'invalid response status \'{type.name}\'' })


