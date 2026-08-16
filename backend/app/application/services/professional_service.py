from app.domain.repositories.care_area_repository import (
    CareAreaRepository,
)
from app.domain.repositories.professional_repository import (
    ProfessionalRepository,
)
from app.infrastructure.database.models.professional import Professional


class ProfessionalNotFoundError(Exception):
    pass


class ProfessionalCareAreaNotFoundError(Exception):
    pass


class ProfessionalService:

    def __init__(
        self,
        professional_repository: ProfessionalRepository,
        care_area_repository: CareAreaRepository,
    ):
        self.professional_repository = professional_repository
        self.care_area_repository = care_area_repository

    async def list_professionals(
        self,
        care_area_id: int | None = None,
    ) -> list[Professional]:

        if care_area_id is not None:

            area = await self.care_area_repository.get_by_id(
                care_area_id
            )

            if area is None:
                raise ProfessionalCareAreaNotFoundError(
                    f"Care area with id {care_area_id} was not found."
                )

        return await self.professional_repository.get_all(
            care_area_id=care_area_id
        )

    async def get_professional(
        self,
        professional_id: int,
    ) -> Professional:

        professional = (
            await self.professional_repository.get_by_id(
                professional_id
            )
        )

        if professional is None:
            raise ProfessionalNotFoundError(
                f"Professional with id {professional_id} was not found."
            )

        return professional

    async def create_professional(
        self,
        care_area_id: int,
        first_name: str,
        last_name: str,
        license_number: str | None = None,
        phone: str | None = None,
    ) -> Professional:

        area = await self.care_area_repository.get_by_id(
            care_area_id
        )

        if area is None:
            raise ProfessionalCareAreaNotFoundError(
                f"Care area with id {care_area_id} was not found."
            )

        professional = Professional(
            care_area_id=care_area_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            license_number=license_number,
            phone=phone,
            active=True,
        )

        return await self.professional_repository.create(
            professional
        )