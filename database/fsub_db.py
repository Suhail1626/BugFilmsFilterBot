import motor.motor_asyncio
from sample_info import tempDict
from info import AUTH_CHANNEL
from typing import Union

class Fsub_DB:
    """
    A class representing a MongoDB database client for managing information of users who have sent join requests.

    Attributes:
        client (motor.motor_asyncio.AsyncIOMotorClient): The MongoDB client.
        db (motor.motor_asyncio.AsyncIOMotorDatabase): The MongoDB database.
        col (motor.motor_asyncio.AsyncIOMotorCollection): The MongoDB collection representing the users.

    Methods:
        __init__: Initializes the MongoDB client, database, and collection.
        add_user: Adds a new user to the collection.
        get_user: Retrieves user information based on the user ID.
        get_all: Retrieves all users.
        delete_user: Deletes a user based on the user ID.
        purge_all: Deletes all users from the collection.
        total_users: Retrieves the total number of users in the collection.
    """

    def __init__(self) -> None:
        """
        Initializes the MongoDB client, database, and collection.

        Connects to the MongoDB server specified in the 'indexDB' field of the 'tempDict' dictionary.
        The collection name is derived from the 'AUTH_CHANNEL' constant.
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(tempDict.get("indexDB"))
        self.db = self.client["Fsub_DB"]
        self.col = self.db[str(AUTH_CHANNEL)]

    async def add_user(self, user_id: Union[int, str], first_name: str, user_name: str, date: str) -> None:
        """
        Adds a new user to the collection.

        Args:
            user_id (int | str): The unique identifier of the user.
            first_name (str): The first name of the user.
            user_name (str): The username of the user.
            date (str): The date of the join request.

        Returns:
            None
        """
        await self.col.insert_one({"id": int(user_id), "fname": first_name, "uname": user_name, "date": date})

    async def get_user(self, user_id: Union[int, str]) -> Union[dict, None]:
        """
        Retrieves user information based on the user ID.

        Args:
            user_id (int | str): The unique identifier of the user.

        Returns:
            dict | None: A dictionary containing user information if found, else None.
        """
        return await self.col.find_one({"id": int(user_id)})
    
    async def get_all(self) -> Union[list, None]:
        """
        Retrieves all users.

        Returns:
            list | None: A list of dictionaries containing all users if found, else None.
        """
        return await self.col.find().to_list(length=None)
    
    async def delete_user(self, user_id: Union[int, str]) -> None:
        """
        Deletes a user based on the user ID.

        Args:
            user_id (int | str): The unique identifier of the user.

        Returns:
            None
        """
        await self.col.delete_one({"id": int(user_id)})

    async def purge_all(self) -> None:
        """
        Deletes all users from the collection.

        Returns:
            None
        """
        await self.col.delete_many({})

    async def total_users(self) -> Union[int, None]:
        """
        Retrieves the total number of users in the collection.

        Returns:
            int | None: The total number of users if found, else None.
        """
        return await self.col.count_documents({})