import math
from unicodedata import east_asian_width
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()

LARGURA, ALTURA = 650, 650
janela = pygame.display.set_mode((LARGURA, ALTURA))

def calculaDistancia(ponto1, ponto2):
  return math.sqrt((ponto2[1] - ponto1[1])**2 + (ponto2[0] - ponto1[0])**2)

def calculaAngulo(ponto1, ponto2):
  return math.atan2(ponto2[1] - ponto1[1] , ponto2[0] - ponto1[0])

def desenho(espaco, janela, opcoesDesenho, linha):
  janela.fill('white')

  if linha:
    pygame.draw.line(janela, 'green', linha[0], linha[1], 3)
    
  espaco.debug_draw(opcoesDesenho)
  pygame.display.update()

def criaFronteiras(espaco, largura, altura):
  retangulos = [
    [(largura/2, altura - 10), (largura, 20)], # chão
    [(largura/2, 10), (largura, 20)], # teto
    [(10, altura/2), (20, altura)], # parede
    [(largura - 10, altura/2), (20, altura)] # parede
  ]

  for pos, tamanho in retangulos:
    corpo = pymunk.Body(body_type=pymunk.Body.STATIC)
    corpo.position = pos
    forma = pymunk.Poly.create_box(corpo, tamanho)
    forma.elasticity = 0.4
    forma.friction = 0.5
    espaco.add(corpo, forma)

def criaEstrutura(espaco, largura, altura):
  MARRON = (139, 69, 19, 100)
  retangulos = [
    [(300, altura - 120), (40, 200), MARRON, 100],
    [(600, altura - 120), (40, 200), MARRON, 100],
    [(450, altura - 240), (340, 40), MARRON, 150]
  ]

  for posicao, tamanho, cor, massa in retangulos:
    corpo = pymunk.Body()
    corpo.position = posicao
    forma = pymunk.Poly.create_box(corpo, tamanho, radius=10)
    forma.color = cor
    forma.mass = massa
    forma.elasticity = 0.4
    forma.friction = 0.4
    espaco.add(corpo, forma)

def criaPendulo(espaco):
  prego = pymunk.Body(body_type=pymunk.Body.STATIC)
  prego.position = (-100, -50)

  corpo = pymunk.Body()
  corpo.posicao = (300, 300)

  haste = pymunk.Segment(corpo, (325, 100), (325, 250), 5)
  esfera = pymunk.Circle(corpo, 40, (325, 250))

  haste.friction = 1
  esfera.friction = 1
  haste.mass = 8
  esfera.mass = 30
  esfera.elasticity = 0.95
  
  juncaoCentroRotacao = pymunk.PinJoint(corpo, prego, (325, 100), (325, 100))
  espaco.add(esfera, haste, corpo, juncaoCentroRotacao)

def criaBola(espaco, raio, massa, posicao):
  corpo = pymunk.Body(body_type=pymunk.Body.STATIC)
  corpo.position = posicao
  forma = pymunk.Circle(corpo, raio)
  forma.mass = massa
  forma.elasticity = 0.9
  forma.friction = 0.5
  forma.color = (255, 0, 0, 100)
  espaco.add(corpo, forma)
  return forma

def run(janela, largura, altura):
  run = True
  relogio = pygame.time.Clock()
  fps = 60
  deltaTime = 1 / fps
  posicaoPressionado = None
  bola = None

  espaco = pymunk.Space()
  espaco.gravity = (0, 981)

  criaFronteiras(espaco, altura, largura)
  criaEstrutura(espaco, largura, altura)
  criaPendulo(espaco)

  opcoesDesenho = pymunk.pygame_util.DrawOptions(janela)

  while run:
    linha = None
    if bola and posicaoPressionado:
      linha = [posicaoPressionado, pygame.mouse.get_pos()]
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False
        break

      if event.type == pygame.MOUSEBUTTONDOWN:
        if not bola:
          posicaoPressionado = pygame.mouse.get_pos()
          bola = criaBola(espaco, 30, 10, posicaoPressionado)
        elif posicaoPressionado:
          bola.body.body_type = pymunk.Body.DYNAMIC
          angulo = calculaAngulo(*linha)
          forca = calculaDistancia(*linha) * 100
          forcaX = math.cos(angulo) * forca
          forcaY = math.sin(angulo) * forca
          bola.body.apply_impulse_at_local_point((forcaX, forcaY), (0, 0))
          posicaoPressionado = None
        else:
          espaco.remove(bola, bola.body)
          bola = None
    
    desenho(espaco, janela, opcoesDesenho, linha)
    espaco.step(deltaTime)
    relogio.tick(fps)
  
  pygame.quit()

if __name__ == "__main__":
  run(janela, LARGURA, ALTURA)