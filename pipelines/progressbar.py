#!/usr/bin/env python
import sys
from ipywidgets import IntProgress, HTML, VBox
from IPython.display import display

class Progressbar():
    """
    A class which can be used to represent a task's progress in the form of a progress bar

    """
    def __init__(self, total=100, steps=100):
        self.percentage = 0
        self.completed = 0
        self.total = int(total)
        self.steps = int(steps)
        sys.stdout.write('\r[{}]'.format('.' * self.steps))
        
    def update_progress(self, progress):
        self.completed += progress
        percentage = int(self.completed/self.total*100)
        if percentage != self.percentage:
            self.percentage = percentage
            steps = int(self.completed/self.total * self.steps)
            sys.stdout.write('\r[{}{}] {} %'.format('█' * steps, '.' * (self.steps-steps),self.percentage))
            sys.stdout.flush()
            if self.percentage >= 100:
                print('\n')
            
            
def log_progress(sequence, every=None, size=None, name='Items'):
    """
    Widget based progress bar for Jupyter, source: https://github.com/kuk/log-progress
    (requires the jupyter lab extension to be installed: $jupyter labextension install @jupyter-widgets/jupyterlab-manager)

    """
    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)     # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except:
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )