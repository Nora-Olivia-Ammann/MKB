from sourcetree_code.tools.x_import import Imp


class Ret:

    @staticmethod
    def ret_ret():
        val = Imp.ret()
        return f"Return {val}"

