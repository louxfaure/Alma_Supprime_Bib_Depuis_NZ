#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import re
# import requests
from datetime import datetime, timedelta
import logging

#Modules maison
from logs import logs

from Alma_Apis_Interface import Alma_Apis

# Initilalisation des paramètres 
service="Suppression des notices sans inventaires de la KB"
niveau_logs = 'DEBUG'
identifie_job_id='M58'
suppr_bib_job_id='M28'

# nom_job_identification_notice = 'Identifier les notices qui ne sont pas utilisées dans le Réseau - Notices avec PPN (marc 21 et unimarc) - Planifié'
nom_job_identification_notice = 'Identifier les notices qui ne sont pas utilisées dans le Réseau - Notice Marc 21 sans PPN - Planifié'

logs_rep = os.getenv('LOGS_PATH')

#On initialise le logger
logs.setup_logging(name=service, level=niveau_logs,log_dir=logs_rep)
log_module = logging.getLogger(service)


def calcule_date_du_traitement():
    aujourdhui = datetime.now()
    jours_a_retrancher = (aujourdhui.weekday() + 1) % 7
    dimanche_precedent = aujourdhui - timedelta(days=jours_a_retrancher)
    return dimanche_precedent

def retrouve_job(job_id,nom_job_identification_notice):
    date_from = calcule_date_du_traitement()
    date_to = date_from
    # date_from = '2024-11-25'
    # date_to = '2024-12-5'
    jobs_list= api.get_job(job_id,date_from,date_to)
    if jobs_list['total_record_count'] == 0 :
        log_module.error("Pas de trace d'exécution du job")
        exit(1)
    elif jobs_list['total_record_count'] == 1 :
        return jobs_list['job_instance'][0]["id"]
    else :
        for job in jobs_list['job_instance'] :
            if  json.loads(f'"{job["name"]}"') == nom_job_identification_notice:
                log_module.debug(job["id"])    
                return job["id"]                


def get_job_parameters(file_name):
    dossier = os.path.dirname(os.path.abspath(__file__))
    file_name = dossier + '/' + file_name
    with open(file_name, 'r',encoding='utf-8') as file:
        job_parameters = json.load(file)
    return job_parameters

def get_job(job_id,instance_id):
    #Interroge un job toutes les 2 minutes et retourne le rapport quand ce dernier est terminé
    detail_service = api.get_job_instances(job_id,instance_id)
    statut = detail_service['status']['value']
    log_module.debug("[get_job (Job ({}) Instance ({}))] Statut ({})".format(job_id,instance_id, statut))
    
    if statut == 'COMPLETED_SUCCESS':
        log_module.debug(json.dumps(detail_service, indent=4, sort_keys=True))
        log_module.info('[number_of_set_members] {} notices sans inventaire dans le réseau'.format(detail_service['counter'][1]['value']))
        return detail_service['counter'][0]['value']
    else:
        log_module.error("[get_job (Job ({}) Instance ({}))] Statut ({})".format(job_id,instance_id, statut))
        exit(1)

def post_job(job_id,job_parameters):
    #Lance un job et retourne l'id de l'instance
    job_reponse = api.post_job(job_id,json.dumps(job_parameters))
    #Récupère l'identifiant du service
    job_service = (job_reponse['additional_info']['link'])
    a = re.search("jobs\/(.*?)\/instances\/(.*)",job_service)
    job_instance_id = a.group(2)
    return job_instance_id

#On initialise l'objet API
api = Alma_Apis.Alma(apikey=os.getenv('PROD_NETWORK_CONF_API'), region='EU', service=service)

date_traitement = calcule_date_du_traitement()
log_module.info(date_traitement.strftime('%Y-%m-%d'))
#On récupère l'indentifinat de l'instance du traitement
instance_job_id = retrouve_job(identifie_job_id,nom_job_identification_notice)
log_module.info('[retrouve_job] Instance Id({})'.format(instance_job_id))
set_name = get_job(identifie_job_id,instance_job_id)
#On récupère l'identifiant du set
search_set_id = api.get_set_id(set_name)
log_module.info('[search_set_id] Succés Identifiant du set des notices à supprimer ({})'.format(search_set_id))

#On lance la suppression des notices du set
suppr_bib_job_parameters = get_job_parameters('./Jobs_parameters/Supprime_notices_Job_Paramater.json')
suppr_bib_job_parameters['parameter'][2]['value'] = search_set_id
suppr_bib_job_instance_id = post_job(suppr_bib_job_id,suppr_bib_job_parameters)
log_module.info('[post_job (Job ({})] Instance Id({})'.format(suppr_bib_job_id,suppr_bib_job_instance_id))
log_module.info('FIN DU TRAITEMENT')