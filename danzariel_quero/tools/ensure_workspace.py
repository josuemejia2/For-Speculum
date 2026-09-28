from danzariel_quero.services.files import ensure_workspace
from danzariel_quero.core.config import settings


def main() -> None:
    ensure_workspace()
    print(f"Workspace listo: {settings.data_dir}")


if __name__ == "__main__":
    main()
