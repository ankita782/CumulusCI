import base64
import os
import json
from typing import Dict
from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.core.exceptions import CumulusCIException
from cumulusci.core.utils import process_list_of_pairs_dict_arg


class UploadProfilePhoto(BaseSalesforceApiTask):
    task_docs = """
    Uploads a profile photo for the default CumulusCI user.

    Example
    *******

    Upload a user profile photo for a user whose ``Alias`` equals ``grace``.:: yaml

        tasks:
            upload_profile_photo:
                group: Internal storytelling data
                class_path: cumulusci.tasks.salesforce.UploadDefaultUserProfilePhoto
                description: Uploads profile photo for the default user.
                options:
                    photo_path: datasets/users/default/profile.png
    """

    task_options = {
        "photo": {"description": "Path to user's profile photo.", "required": True},
        "filters": {
            "description": """List of key/value pairs of User fields and values to filter for a unique User whom to upload the profile photo for.
            - Key/value filters are joined with an "AND" in the generated SOQL query.
            - The SOQL query must return one and only one User record.
            - If no filters are supplied, uploads the photo for the org's default User.
            """,
            "required": False,
        },
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)
        self._filters = process_list_of_pairs_dict_arg(self.options.get("filters", {}))

    def _get_user_fields(self) -> Dict[str, str]:
        user_fields = {}
        for field in self.sf.User.describe()["fields"]:
            user_fields[field["name"]] = field
        return user_fields

    def _get_query(self, filters: Dict[str, object]) -> str:
        user_fields = self._get_user_fields()
        string_soap_types = ("xsd:string", "tns:ID", "urn:address")

        query_filters = []
        for name, value in filters.items():
            field = user_fields.get(name)

            # Validate field exists.
            if not field:
                raise CumulusCIException(
                    f'User Field "{name}" referenced in "filters" option is not found.  Fields are case-sensitive.'
                )

            # Validate we can filter by field.
            if not field["filterable"]:
                raise CumulusCIException(
                    f'User Field "{name}" referenced in "filters" option must be filterable.'
                )

            if field["soapType"] in string_soap_types:
                query_filters.append(f"{name} = '{value}'")
            else:
                query_filters.append(f"{name} = {value}")

        return "SELECT Id FROM User WHERE {}".format(" AND ".join(query_filters))

    def _get_user_id_by_query(self, filters: Dict[str, object]) -> str:
        # Query for the User.
        query = self._get_query(self._filters)
        self.logger.info(f"Querying User: {query}")

        user_ids = []
        for record in self.sf.query_all(query)["records"]:
            user_ids.append(record["Id"])

        # Validate only 1 User found.
        if len(user_ids) < 1:
            raise CumulusCIException("No Users found.")
        if 1 < len(user_ids):
            raise CumulusCIException(
                "More than one User found ({}): {}".format(
                    len(user_ids), ", ".join(user_ids)
                )
            )

        # Log and return User ID.
        self.logger.info(f"Uploading profile photo for the User with ID {user_ids[0]}.")
        return user_ids[0]

    def get_default_user_id(self) -> str:
        user_id = self.sf.restful("")["identity"][-18:]
        self.logger.info(
            f"Uploading profile photo for the default User with ID {user_id}."
        )
        return user_id

    def _run_task(self):
        # Get the User Id of the targeted user.
        user_id = (
            self._get_user_id_by_query(self._filters)
            if self._filters
            else self._get_default_user_id()
        )

        # Upload profile photo ContentDocument.
        path = self.options["photo"]

        self.logger.info(f"Setting user photo to {path}")
        with open(path, "rb") as version_data:
            result = self.sf.ContentVersion.create(
                {
                    "PathOnClient": os.path.split(path)[-1],
                    "Title": os.path.splitext(os.path.split(path)[-1])[0],
                    "VersionData": base64.b64encode(version_data.read()).decode(
                        "utf-8"
                    ),
                }
            )
            if not result["success"]:
                raise CumulusCIException(
                    "Failed to create ContentVersion: {}".format(result["errors"])
                )
            content_version_id = result["id"]

        # Query the ContentDocumentId for our created record.
        content_document_id = self.sf.query(
            f"SELECT Id, ContentDocumentId FROM ContentVersion WHERE Id = '{content_version_id}'"
        )["records"][0]["ContentDocumentId"]

        self.logger.info(
            f"Uploaded profile photo ContentDocument {content_document_id}."
        )

        # Call the Connect API to set our user photo.
        result = self.sf.restful(
            f"connect/user-profiles/{user_id}/photo",
            data=json.dumps({"fileId": content_document_id}),
            method="POST",
        )
