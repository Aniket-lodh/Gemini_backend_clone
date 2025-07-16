import logging
import traceback
from fastapi import HTTPException, status
from src.core.db_models import (
    Chatrooms,
    Messages,
    Password,
    TableNameEnum,
    Transactions,
    UserPlan,
    UserProfile,
    Users,
)
from typing import List, Optional, Tuple, TypeVar, Union
from sqlmodel import SQLModel, Session, or_, select
from sqlalchemy.exc import IntegrityError

T = TypeVar("T", bound=SQLModel)
logger = logging.getLogger(__name__)


class DB:
    def __init__(self):
        pass

    def _upsert_commit(
        self, data: Union[T, List[T]], commit: bool, db_pool: Session
    ) -> SQLModel | list[SQLModel]:
        """
        Upsert one or more objects into the database based on primary key.

        If a single object is passed, a single merged instance is returned.
        If a list of objects is passed, a list of merged instances is returned.

        Parameters:
            data (Union[T, List[T]]): Single SQLModel instance or list of instances
            commit (bool): Whether to commit the transaction and refresh the objects
            db_pool (Session): The SQLModel session.

        Returns:
            :SQLModel | list[SQLModel]: The upserted and optionally refreshed object(s)

        Raises:
            :TypeError: If data is not a SQLModel instance or a list of SQLModel instances

        Example:
           - Upsert a single ORGANIZATIONS instance:
            >>> org = ORGANIZATIONS(oid="123", email="test@example.com")
            >>> updated_org = self._upsert_commit(data=org, commit=True, db_pool=db_pool)
            >>> print(updated_org.email)

        - Upsert multiple ORGANIZATIONS instances:
        >>> orgs = [
        ...     ORGANIZATIONS(oid="123", email="test@example.com"),
        ...     ORGANIZATIONS(oid="1234", email="test1@example.com")
        ... ]
        >>> updated_orgs = self._upsert_commit(data=orgs, commit=True, db_pool=db_pool)
        >>> for org in updated_orgs:
        ...     print(org.oid, org.email)
        """

        if isinstance(data, list):
            if not all(isinstance(item, SQLModel) for item in data):
                raise TypeError("All items must be SQLModel instances")
            objects = data
        else:
            if not isinstance(data, SQLModel):
                raise TypeError("Data must be a SQLModel instance")
            objects = [data]

        merged_objects = [db_pool.merge(obj) for obj in objects]
        if commit:
            db_pool.commit()
            for obj in merged_objects:
                db_pool.refresh(obj)

        return merged_objects[0] if len(merged_objects) == 1 else merged_objects

    async def insert(
        self,
        dbClassName: TableNameEnum,
        data: dict,
        db_pool: Session,
        commit: bool = False,
    ) -> Tuple[Optional[Users | Password | Messages | UserPlan | None], bool]:
        """
        Insert a new record into the database for the specified table.

        This method creates an instance of the appropriate SQLModel based on the `dbClassName` enum,
        and inserts it into the database using an upsert operation. If a record with the same primary key
        already exists, it will be updated instead. Optionally commits and refreshes the object.

        Parameters:
            dbClassName (TableNameEnum): Enum value representing the target table/model.
            data (dict): Dictionary of field values used to initialize the model instance.
            db_pool (Session): SQLAlchemy session object for database interaction.
            commit (bool, optional): If True, commits the transaction and refreshes the object. Defaults to False.

        Returns:
            :Tuple[Optional[SQLModel], bool]:
                - The inserted SQLModel instance (or None if failed).
                - A boolean indicating success (True) or failure (False).
        """

        try:
            if dbClassName == TableNameEnum.Users:
                data = Users(**data)
            elif dbClassName == TableNameEnum.Password:
                data = Password(**data)
            elif dbClassName == TableNameEnum.Chatrooms:
                data = Chatrooms(**data)
            elif dbClassName == TableNameEnum.Messages:
                data = Messages(**data)
            elif dbClassName == TableNameEnum.UserProfile:
                data = UserProfile(**data)
            elif dbClassName == TableNameEnum.Transactions:
                data = Transactions(**data)
            elif dbClassName == TableNameEnum.UserPlan:
                data = UserPlan(**data)
            else:
                return None, False

            self._upsert_commit(data=data, db_pool=db_pool, commit=commit)
            return data, True
        except IntegrityError as e:
            if "ix_users_email" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            if "ix_users_mobile_number" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Mobile number already registered",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate entry",
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

    async def update(
        self,
        dbClassName: TableNameEnum,
        data: dict,
        db_pool: Session,
        commit: bool = False,
    ) -> Tuple[
        Optional[Users | Messages | Transactions | None],
        bool,
    ]:
        """
        Update a single database record by upserting the provided data based on primary key.

        This method dynamically instantiates the appropriate SQLModel based on the table enum,
        then performs an upsert operation (insert or update). If `commit=True`, the transaction
        is committed and the returned object is refreshed to reflect the latest database state.

        Parameters:
            dbClassName (TableNameEnum): Enum representing the target table.
            data (dict): Dictionary of data corresponding to the target table's model fields.
            db_pool (Session): SQLAlchemy session object.
            commit (bool, optional): Whether to commit the transaction and refresh the object. Defaults to False.

        Returns:
           :Tuple[Optional[SQLModel], bool]:
                A tuple containing:

                - The upserted SQLModel instance, or `None` if an error occurs.
                - A boolean indicating the success (`True`) or failure (`False`) of the operation.
        """

        try:
            if dbClassName == TableNameEnum.Users:
                data = Users(**data)
            elif dbClassName == TableNameEnum.Messages:
                data = Messages(**data)
            elif dbClassName == TableNameEnum.Transactions:
                data = Transactions(**data)
            else:
                return None, False
            data = self._upsert_commit(data=data, db_pool=db_pool, commit=commit)
            return data, True
        except IntegrityError as e:
            if "ix_users_email" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
            if "ix_users_mobile_number" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Mobile number already registered",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate entry",
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

    async def get_attr_all(
        self,
        dbClassName: TableNameEnum,
        uid: str = None,
        limit: Optional[int | str] = 1,
        offset: Optional[int] = 0,
        order_by: Optional[str] = "desc",
        db_pool: Session = None,
    ) -> list[Chatrooms]:
        try:
            table = None
            if dbClassName == TableNameEnum.Chatrooms:
                statement = (
                    select(Chatrooms)
                    .where(Chatrooms.owner_id == uid)
                    .limit(limit if limit != "*" else None)
                    .offset(offset)
                )
                if order_by == "asc":
                    statement = statement.order_by(Chatrooms.created_at.asc())
                else:
                    statement = statement.order_by(Chatrooms.created_at.desc())
                table = db_pool.exec(statement).all()

            return table

        except Exception as e:
            if isinstance(db_pool, Session):
                db_pool.rollback()
                traceback.print_exc()
            return None

    async def get_attr(
        self,
        dbClassName: TableNameEnum,
        mobile_number: str = None,
        uid: str = None,
        mid: str = None,
        customer_id: str = None,
        chatroom_id: str = None,
        transaction_id: str = None,
        db_pool: Session = None,
    ) -> Optional[Users | Chatrooms | Messages | Transactions | None]:
        try:
            table = None
            if dbClassName == TableNameEnum.Users:
                statement = select(Users)
                if uid:
                    statement = statement.where(Users.uid == uid)
                if mobile_number:
                    statement = statement.where(Users.mobile_number == mobile_number)
                if customer_id:
                    statement = statement.where(Users.stripe_customer_id == customer_id)

            if dbClassName == TableNameEnum.Chatrooms:
                statement = select(Chatrooms)
                if uid:
                    statement = statement.where(Chatrooms.owner_id == uid)
                if chatroom_id:
                    statement = statement.where(Chatrooms.chatroom_id == chatroom_id)

            if dbClassName == TableNameEnum.Messages:
                statement = select(Messages)
                if uid:
                    statement = statement.where(Messages.sender_id == uid)
                if mid:
                    statement = statement.where(Messages.mid == mid)

            if dbClassName == TableNameEnum.Transactions:
                statement = select(Transactions)
                if transaction_id:
                    statement = statement.where(
                        Transactions.transaction_id == transaction_id
                    )

            table = db_pool.exec(statement).first()
            return table
        except Exception as e:
            if isinstance(db_pool, Session):
                db_pool.rollback()
                traceback.print_exc()
            return None
