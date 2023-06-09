from fastapi import HTTPException, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.manager import current_active_user
from src.database import get_async_session
from src.fault.services import get_fault, get_image
from src.project.dependencies import valid_project
from src.project.models import Project

MAX_SIZE = 1024 * 1024 * 10  # 10 megabytes


def valid_image(file: UploadFile):
    if not file.content_type in ['image/jpeg', 'image/gif', 'image/png']:
        raise HTTPException(status_code=418, detail="It isn't jpeg or gif or png.")
    if file.size > MAX_SIZE:
        raise HTTPException(status_code=419, detail="The file size cannot be greater than 10 megabytes.")
    return file


async def valid_fault(
        fault_id: int,
        project: Project = Depends(valid_project),
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user),
):
    fault = await get_fault(fault_id, session)
    if not fault or fault.creator_id != user.id or fault.project_id != project.id:
        raise HTTPException(status_code=404, detail="Not found.")
    return fault


async def valid_image_path(
        image_id: int,
        fault_id: int,
        session: AsyncSession = Depends(get_async_session),
        user=Depends(current_active_user)
):
    image = await get_image(image_id, session)
    if not image or image.fault_id != fault_id:
        raise HTTPException(status_code=404, detail="Not found.")
    fault = await get_fault(image.fault_id, session)
    if fault.creator_id != user.id:
        raise HTTPException(status_code=404, detail="Not found.")
    return f'media/{user.id}/{image.file_name}'