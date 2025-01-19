from fastapi import APIRouter

router = APIRouter(
    prefix="/users"
)

@router.post("/register")
def registrer(request):
    pass