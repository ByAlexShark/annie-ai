import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.care_area import CareArea
from app.infrastructure.database.models.service import Service
from app.infrastructure.database.session import AsyncSessionLocal


CATALOG = {
    "Enfermería": [
        "Sueroterapia",
        "Inyectables",
        "Perforación",
        "Enfermera a domicilio",
        "Curaciones",
    ],
    "Cirugías": [
        "Vesícula",
        "Hernia",
        "Apéndice",
    ],
    "Medicina General": [
        "Curaciones",
        "Consulta",
        "A domicilio",
        "Urgencias",
    ],
    "Ecografía": [
        "Abdominal – transvaginal",
        "Neonatal",
    ],
    "Podología": [
        "Retiro de verrugas",
        "Verrugas plantares",
        "Uñeros",
        "Hongos",
        "Onicomicosis",
        "Ozono – láser",
    ],
    "Especialidades Médicas": [
        "Ginecología",
        "Cardiología",
        "Traumatología",
        "Neurología",
        "Otorrinolaringología",
        "Pediatría",
        "Urología",
        "Endocrinología",
    ],
    "Laboratorio": [
        "H. Pylori",
        "Exámenes de drogas",
        "Orina",
        "Sangre",
    ],
    "Estética": [
        "Limpieza facial",
        "PRP facial – capilar",
        "Plasma Pen",
    ],
    "Fisioterapia": [
        "Rodilla",
        "Hombro",
        "Rehabilitación",
        "Maderoterapia",
        "Patologías (DBT)",
        "Lumbalgia",
        "Masajes relajantes",
    ],
    "CES / Salud Mental": [
        "Psicología",
        "Psiquiatría",
        "Terapia de parejas",
        "TDAH",
        "Autismo",
        "Ansiedad",
        "TCA",
        "Adicciones",
    ],
}


AREA_DESCRIPTIONS = {
    "Enfermería": "Servicios generales de enfermería.",
    "Cirugías": "Procedimientos quirúrgicos disponibles en el centro.",
    "Medicina General": "Atención de medicina general y urgencias.",
    "Ecografía": "Servicios de diagnóstico mediante ecografía.",
    "Podología": "Atención y tratamiento especializado del pie.",
    "Especialidades Médicas": "Área que agrupa las especialidades médicas del centro.",
    "Laboratorio": "Servicios y pruebas de laboratorio clínico.",
    "Estética": "Servicios de estética y cuidado personal.",
    "Fisioterapia": "Servicios de fisioterapia y rehabilitación.",
    "CES / Salud Mental": "Servicios psicológicos, psiquiátricos y de salud mental.",
}


async def get_or_create_area(
    session: AsyncSession,
    name: str,
) -> tuple[CareArea, bool]:

    result = await session.execute(
        select(CareArea).where(CareArea.name == name)
    )

    area = result.scalar_one_or_none()

    if area is not None:
        return area, False

    area = CareArea(
        name=name,
        description=AREA_DESCRIPTIONS.get(name),
        active=True,
    )

    session.add(area)

    # Necesitamos el ID antes de crear los servicios.
    await session.flush()

    return area, True


async def service_exists(
    session: AsyncSession,
    area_id: int,
    service_name: str,
) -> bool:

    result = await session.execute(
        select(Service).where(
            Service.area_id == area_id,
            Service.name == service_name,
        )
    )

    return result.scalar_one_or_none() is not None


async def seed_catalog() -> None:

    created_areas = 0
    created_services = 0

    async with AsyncSessionLocal() as session:

        try:
            for area_name, services in CATALOG.items():

                area, was_created = await get_or_create_area(
                    session,
                    area_name,
                )

                if was_created:
                    created_areas += 1

                for service_name in services:

                    if await service_exists(
                        session,
                        area.id,
                        service_name,
                    ):
                        continue

                    service = Service(
                        area_id=area.id,
                        name=service_name,
                        default_duration_minutes=30,
                        price=None,
                        currency="BOB",
                        active=True,
                    )

                    session.add(service)
                    created_services += 1

            await session.commit()

            print("ANNIE AI - Catálogo institucional cargado")
            print(f"Áreas nuevas: {created_areas}")
            print(f"Servicios nuevos: {created_services}")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_catalog())
