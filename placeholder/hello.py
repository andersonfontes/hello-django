import sys

from django.conf import settings

# essa configuração coloca em modo debugging e inclui uma SECRET KEY não-aletoria, que nao deverá ser usada no ambiente de produção
# uma chave secreta devará sergerada para a sessão default para a proteção contra CSRF (Cross-Site Request Forgery). É importante que qualquer site de proução tenha uma secret key aleatoria que permaneça privada. Para saber mais sobre esse assunto acesse documentação: https://docs.djangoproject.com/en/1.7/topics/signing
settings.configure(
    DEBUG=True,
    SECRET_KEY="thisisthesecretkey",
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.middleware.cickjacking.XFrameOptionsMiddleware",
    ),
)

# precisamos definir as configurações antes de fazer qualquer importação no Django, pois algumas partes do framework esperam que as configurações estejam definidas antes de poderem ser importadas. Normalmente isso não será um problema, pois estas configurações estarão incluídas no arquivo settings.py. O arquivo gerado pelo comando startproject tambémincluirá configurações para itens que não serão usados neste exemplo, ex.: internacionalização e recursos estáticos


from django.urls import include, re_path

# from django.conf import url
# Para conectar nossa view à estrutura do site,devemos asssociá-la a um padrão de URL. Neste exemplo, a própria raiz do servidor pode servir a view. O Django associa views a seus URLS ao combiná-las com uma expressão regular que corresponda ao URL e qualquer argumento que possa ser chamado com a view.

from django.http import HttpResponse

# O django é MTv - A parte referente a VIEW normalmente inspeciona a solicitação HTTP de entrada e faz queries ou compõeos dados necessários a serem enviados à camada de apresentação


# def index(request):
#     banana = "color:blue;"
#     return HttpResponse(f"<h1>Titulo</h1><h2 style={banana}>eu sou um h2</h2>")


urlpatterns = (re_path(r"^$", index),)

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
