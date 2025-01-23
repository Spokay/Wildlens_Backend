from fastapi import APIRouter

router = APIRouter(
    prefix="/users"
)

@router.post("/register")
def registrer(request):
    pass

@router.post("/login")
def login(request):
    pass