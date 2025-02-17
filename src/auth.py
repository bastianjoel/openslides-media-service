import requests

from .exceptions import ServerError

AUTH_HEADER = "Authentication"


def check_file_id(file_id, file_type, app, presenter_headers):
    """
    Returns a triple: ok, filename, auth_header.
    filename is given, if ok=True. If ok=false, the user has no perms.
    if auth_header is returned, it must be set in the response.
    """
    presenter_url = get_presenter_url(app)
    if file_type == "mediafile":
        payload = [
            {"presenter": "check_mediafile_id", "data": {"mediafile_id": file_id}}
        ]
    elif file_type == "resource":
        payload = [{"presenter": "check_resource_id", "data": {"resource_id": file_id}}]
    app.logger.debug(f"Send check request: {presenter_url}: {payload}")

    try:
        response = requests.post(presenter_url, headers=presenter_headers, json=payload)
    except requests.exceptions.ConnectionError as e:
        app.logger.error(str(e))
        raise ServerError("The server didn't respond")

    if response.status_code != requests.codes.ok:
        raise ServerError(
            "The server responded with an unexpected code "
            f"{response.status_code}: {response.content}"
        )

    # Expects: {ok: bool, filename: Optional[str]}

    try:
        content = response.json()
    except ValueError:
        raise ServerError("The Response does not contain valid JSON.")
    if not isinstance(content, list) or len(content) != 1:
        raise ServerError("The returned json is not a list of length 1.")
    content = content[0]
    if not isinstance(content, dict):
        raise ServerError("The returned content is not a dict.")

    auth_header = response.headers.get(AUTH_HEADER)

    if not content.get("ok", False):
        return False, None, auth_header

    if "filename" not in content:
        raise ServerError("The presenter did not provide a filename")

    return True, content["filename"], auth_header


def get_presenter_url(app):
    presenter_host = app.config["PRESENTER_HOST"]
    presenter_port = app.config["PRESENTER_PORT"]
    return f"http://{presenter_host}:{presenter_port}/system/presenter/handle_request"
