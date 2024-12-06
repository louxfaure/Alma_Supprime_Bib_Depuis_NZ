# logs
Implemnetation de logging pour l'écriture des logs de mes programmes.
Créé une sortie fichier et console.

Grosse inspiration (voir pompage complet) prise chez https://github.com/louxfaure/logs.git et https://docs.python.org/3/howto/logging-cookbook.html


## Paramètres
### logsrep
Répertoire de stockage des logs
### programme
Nom du programme qui écrit les logs. IL va permettre de nommer mon  logger afin de pouvoir l'appeler depuis des modules auxiliares.
Définie aussi le nom du fichier des logs.
### niveau
Niveau des messages à écrire dans les logs.


Niveau | Valeur | Usage
------ | ------ | -----
CRITICAL | 50 | Le programme complet est en train de partir en couille.
ERROR | 40 | Une opération a foirée.
WARNING | 30 | Pour avertir que quelque chose mérite l’attention : enclenchement d’un mode particulier, detection d’une situation rare, un lib optionelle peut être installée.
INFO | 20 | Pour informer de la marche du programme. Par exemple : “Starting CSV parsing”
DEBUG | 10 | Pour dumper des information quand vous débuggez. Par exemple savoir ce qu’il y a dans ce putain de dictionnaire. 

## Utilisation
main.py


    import logging
    import logs 
    programme = 'test_log'
    mode = 'INFO' 
    logs.init_logs('/home/loux/.Alma',programme,mode)
    log_module = logging.getLogger(programme)

    log_module.debug('debug')
    log_module.info('Hello')
    log_module.warning('Atention')

sub_module.py
    import logging
    log_module = logging.getLogger('test_log')

    log_module.debug('debug')
    log_module.info('Hello')
    log_module.warning('Atention')
