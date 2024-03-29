import logging.config

# TODO: PEP 484 Stub Files issue?
from cognite.client import ClientConfig, CogniteClient
from cognite.client.credentials import OAuthClientCredentials
from pydantic import Field, field_validator

from .. import __version__
from ..common.base_model import Model


class CogniteIdpConfig(Model):
    # fields required for OIDC client-credentials authentication
    client_name: str = Field(default=f"inso-extpipes-cli:{__version__}")
    client_id: str
    secret: str
    scopes: list[str]
    token_url: str


class CogniteConfig(Model):
    host: str
    project: str
    idp_authentication: CogniteIdpConfig

    # compatibility properties to keep get_cognite_client() in sync with other solutions
    # which are using flat-property list, no nesting and a bit different names
    @property
    def base_url(self) -> str:
        return self.host

    @property
    def token_url(self) -> str:
        return self.idp_authentication.token_url

    @property
    def scopes(self) -> list[str]:
        return self.idp_authentication.scopes

    @property
    def client_name(self) -> str:
        return self.idp_authentication.client_name or self.client_name

    @property
    def client_id(self) -> str:
        return self.idp_authentication.client_id

    @property
    def client_secret(self) -> str:
        return self.idp_authentication.secret

    @field_validator("host")
    @classmethod
    def host_must_contain_https(cls, v: str) -> str:
        if not v.startswith("https"):
            raise ValueError("must start with https://")
        return v


def get_cognite_client(cognite_config: CogniteConfig) -> CogniteClient:
    """Get an authenticated CogniteClient for the given project and user
    Returns:
        CogniteClient: The authenticated CogniteClient
    """
    try:
        logging.debug("Attempt to create CogniteClient")

        credentials = OAuthClientCredentials(
            token_url=cognite_config.token_url,
            client_id=cognite_config.client_id,
            client_secret=cognite_config.client_secret,
            scopes=cognite_config.scopes,
        )

        cnf = ClientConfig(
            client_name=cognite_config.client_name,
            base_url=cognite_config.base_url,
            project=cognite_config.project,
            credentials=credentials,
        )
        logging.debug(f"get CogniteClient for {cognite_config.project=}")

        return CogniteClient(cnf)
    except Exception as e:
        logging.critical(f"Unable to create CogniteClient: {e}")
        raise
