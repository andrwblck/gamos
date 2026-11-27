"""Збирає index.html: вставляє згенерований світ у шаблон гри."""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import world
src = open(os.path.join(here, 'game.src.html'), encoding='utf-8').read()
out = src.replace('/*WORLD*/', world.export())
open(os.path.join(here, '..', 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html зібрано,', len(out)//1024, 'КБ')
