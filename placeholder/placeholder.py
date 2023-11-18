import hashlib #para usar a soluão com ETag
import os
import sys

from django.conf import settings

DEBUG = os.environ.get('DEBUG','on') == 'on',
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-v7lu7^y3a7*0q4&ne^5po3macl^5v4#2x)ata8ejy0b3)c=#4q')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
BASE_DIR = os.path.dirname(__file__)

#essa configuração coloca em modo debugging e inclui uma SECRET KEY não-aletoria, que nao deverá ser usada no ambiente de produção
#uma chave secreta devará ser gerada para a sessão default para a proteção contra CSRF (Cross-Site Request Forgery). É importante que qualquer site de proução tenha uma secret key aleatoria que permaneça privada. Para saber mais sobre esse assunto acesse documentação: https://docs.djangoproject.com/en/1.7/topics/signing
settings.configure( 
DEBUG = DEBUG,
SECRET_KEY = SECRET_KEY,
ROOT_URLCONF=__name__,
MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
         'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),

INSTALLED_APPS = ('django.contrib.staticfiles',),
TEMPLATE_DIRS =  (os.path.join(BASE_DIR,'templates'),),
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),),
STATIC_URL = '/static/'
)


#precisamos definir as configurações antes de fazer qualquer importação no Django, pois algumas partes do framework esperam que as configurações estejam definidas antes de poderem ser importadas. Normalmente isso não será um problema, pois estas configurações estarão incluídas no arquivo settings.py. O arquivo gerado pelo comando startproject também incluirá configurações para itens que não serão usados neste exemplo, ex.: internacionalização e recursos estáticos
from django.urls import include, re_path, reverse
#from django.conf import url

#formulario de validacao para validar conteudo do POST e do GET
from django import forms 

# Para conectar nossa view à estrutura do site,devemos asssociá-la a um padrão de URL. Neste exemplo, a própria raiz do servidor pode servir a view. O Django associa views a seus URLS ao combiná-las com uma expressão regular que corresponda ao URL e qualquer argumento que possa ser chamado com a view.

from django.core.wsgi import get_wsgi_application

from django.http import HttpResponse , HttpResponseBadRequest
#O django é MTV - A parte referente a VIEW normalmente inspeciona a solicitação HTTP de entrada e faz queries ou compõeos dados necessários a serem enviados à camada de apresentação

from django.views.decorators.http import etag 

from django.core.cache import cache
    # Utilizando caching para reduzir as reuisições - sempre que um novo formato de imagem for gerado sera armazenado em cache, se não tiver no cache ele cria uma novo, se tiver ele usa a aque tem. 
    # Há duas opções em que podemos pensar ao determinar a maneira de utilizar caching nesse serviço: o lado do servidor e o lado do cliente. Para caching do lado do servidor, podemos utilizar facilmente os recursos de cache do Django. Uma troca será feira entre a memória usada para armazenar os valores em cache e os ciclos da CPU necessários para gerar as imagens 

    #generate_etag é uma função nova que recebe os mesmos arg da view placholder. Ela usa o hashlib para retornar um valor opaco de etag, que variará de acordo com valores de width e height
    #a função generate_etag sera passada ao decorador etag na view placeholder

#from django.core.urlresolvers import reverse ---> agora esta na django.urls
    #A view index atualizada cria uma uma URL de exemplo ao usar reverse na view placeholder, e o passa ao contexto do template

from django.shortcuts import render
    #O template home.html é renderizado com o uso do atalho render

def index(request):
    example = reverse('placeholder', kwargs={'width':50,'height':50})
    context = {
        'example': request.build_absolute_uri(example)
    }
    return render (request, 'home.html', context)

def generate_etag(request, width, height):
    content = 'Placeholder: {0} x {1}'.format(width,height)
    return hashlib.sha1(content.encode('utf-8')).hexdigest()

@etag(generate_etag)        
def placeholder(request,width,height):
    #TODO: o restante da view sera inserido aqui
    # return HttpResponse('Ok')
    form = ImageForm( {'height': height , 'width': width} )
    if form.is_valid():
        image = form.generate()
        return HttpResponse(image, content_type='image/png')
        # TODO: GERAR UMA IMAGEM DO TAMANHO SOLICITADO
        return HttpResponse('Ok')
    
    # para criar uma imagem no pillow, dois argumentos sao necessario: o MODO associado à cor e ao tamanho na forma de uma tupla. Essa view usará o modo RGB e o tamanho recebido dos valores validados do form. Ha um 3o argumento nao-obrigatório que define a cor da imagem, que por padrão será preto
    else:
        return HttpResponseBadRequest('Invalid Image Request')

#ROTAS
urlpatterns = (
    # re_path(r'^$', index),
    re_path(r'image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', placeholder, name='placeholder'), 
    re_path(r'^$',index,name='homepage'),
)

application = get_wsgi_application()



from io import BytesIO
from PIL import Image,ImageDraw
    
    
class ImageForm(forms.Form):
    """ Formulário para validar o placeholder da imagem solicitada """
    height = forms.IntegerField(min_value=1, max_value=2000)
    width=forms.IntegerField(min_value=1, max_value=2000)    
        # A view agora pode aceitar e validar a altura e a largura solicitada pelo cliente, porém ainda não está gerando a imagem propriamente dita. Para lidar com a manipulação de imagens no Python nós precisamos instalar o o Pillow, pip install Pillow
        # documentação do pillow: pillow.readthedocs.org

    def generate(self,image_format='PNG'):
        """Gera uma iamgem do tipo especificado e retorna na forma de bytes puros"""
        height = self.cleaned_data['height']
        width = self.cleaned_data['width']
        key = '{}.{}.{}'.format(width,height,image_format) #uma chave de cache é gerada baseada nas dimensoes e tipo da imagem
        content = cache.get(key)
        if content is None: #antes de uma nova imagem ser gerada,o cache é verificado pra saber sea nova imagem já está armazenada
            image = Image.new('RGB', (width,height))
            draw = ImageDraw.Draw(image)
            text = '{} X {}'.format(width,height)
            textwidth, textheight = draw.textsize(text) 
            if textwidth < width and textheight < height:
                texttop = (height - textheight) // 2
                textleft = (width - textwidth) // 2
                draw.text((textleft,texttop), text, fill=(255,255,255))
            content = BytesIO()
            image.save(content,image_format)
            cache.set(key,content,60*60) #imagem que nao estava no cache e foi criada,agora vai ser gravada no cache tambem
            content.seek(0)
        return content
    
    #O default do Django é usar o cache em memória como um processo local, porém com um backend diferente poderá ser usado - por exemplo o Memcached ou o sistema de arquivos - se CACHES for configurado
    #Uma abordagem complementar consiste em focar no comportamento do lado cliente e usar o caching incluído no navegador.O Django inclui um decorador (decorator) etag para usar e gerar cabeçalhos ETag para a view . O decorador recebe um único argumento, que éuma função para gerar o cabeçalho ETag a partir da solicitação e dos argumetnos da view. 





def index(request):
    example = reverse('placeholder', kwargs={'width':50,'height':50})
    context = {
        'example': request.build_absolute_uri(example)
    }
    return render (request, 'home.html', context)

if __name__=="__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

#MAIS SOBRE CACHE COM ETAG - TIRADO DO STACK OVERFLOW:
# De forma sucinta, ETag é um mecanismo do HTTP para validação condicional de cache.

# A ideia é servir conteúdo a ser cacheado com um identificador (geralmente um hash ou número de versão). O cliente então passa a usar esse identificador para perguntar ao servidor se o conteúdo mudou.

# Exemplo
# O request:

# GET /Trj17.png HTTP/1.1
# Host: i.stack.imgur.com
# Recebe a imagem com o header ETag:

# HTTP/1.1 200 OK   
# Content-Type: image/png
# Content-Length: 61404
# ETag: "a5ea8bbcc437de9787e9a87ef6ef690a"

# corpo da imagem
# O cliente então cacheia essa imagem. Quando o usuário requisitar a imagem novamente o cliente pode usar o identificador para "perguntar" ao servidor se a versão em cache ainda é válida:

# GET /Trj17.png HTTP/1.1
# Host: i.stack.imgur.com
# If-None-Match: "a5ea8bbcc437de9787e9a87ef6ef690a"
# Se a versão ainda for válida o servidor volta uma resposta com código 304, indicando que é seguro para o cliente usar a versão em cache:

# HTTP/1.1 304 Not Modified
# ETag: "a5ea8bbcc437de9787e9a87ef6ef690a"
# No caso da imagem ter mudado o servidor responde com código 200, a nova versão da imagem e uma nova ETag.

# Dessa forma, consideramos ETag um mecanismo de validação de cache baseado em conteúdo, em oposição ao par de cabeçalhos Last-Modified e If-Modified-Since que configuram um mecanismo de validação baseado em tempo.

# Ambos os mecanismos de validação são complementares aos headers Cache-Control e Expires que basicamente dizem para o cliente se ele deve ou não cachear um recurso e até quando.

#OUTRA OPÇÃO - DO LIVRO:
# O django.middleware.common.CommonMiddleware , habilitadona seçãoMIDDLEWARE_CLASSES, tambem tem suporte para gerar e usar etags se a configuração USE_ETAGS estiver ativada. Entretanto ha uma difeenreça entre o modo como funciona omiddleware e o decorador. O middleware calculará a Etag de acordo com o hash md5 de conteúdo da resposta. Isso exige que a view faça todo o trabalho de gerar o conteúdo para que a hash seja calculada. O resultado é o mesmo no que concerne ao navegador receber uma respostar 304 Not Modified, proposrcionando economia de largura de banda.Usar o decorador etag tem vantagem de a ETag ser calculada antes de a view ser chamada, oq ue também fará com que o tempo de processamento e recursos sejam economizados