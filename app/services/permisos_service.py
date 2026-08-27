from app.configuracion import PERMISOS_VISTAS


class PermisosPolicy:
    def obtener(self, usuario):
        if usuario.rol and usuario.rol.Nombre == "ADMINISTRADOR":
            return set(PERMISOS_VISTAS)
        return {
            permiso.strip()
            for permiso in (usuario.Permisos or "").split(",")
            if permiso.strip() in PERMISOS_VISTAS
        }

    def puede_acceder(self, usuario, vista):
        return vista in self.obtener(usuario)


def obtener_permisos_usuario(usuario):
    return PermisosPolicy().obtener(usuario)
