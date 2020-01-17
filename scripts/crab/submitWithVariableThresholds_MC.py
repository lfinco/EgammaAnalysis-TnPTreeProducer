#!/bin/env python

### Version of submission ###
submitVersion = "test"



defaultArgs   = ['isMC=True','doEleID=False','doPhoID=False','doTrigger=True', 'GT=94X_mc2017_realistic_v11']
#mainOutputDir = '/store/user/tomc/tnpTuples/%s' % submitVersion # Change to your own
mainOutputDir = '/store/group/phys_egamma/lfinco/2017/L1Matching/%s' % submitVersion
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config
config = config()

config.General.requestName            = '' 
config.General.transferLogs           = False
config.JobType.pluginName             = 'Analysis'

config.JobType.psetName               = '../../python/TnPTreeProducer_cfg.py'
config.JobType.sendExternalFolder     = True

config.Data.inputDataset              = ''
config.Data.inputDBS                  = 'global'
config.Data.publication               = False
config.Data.allowNonValidInputDataset = True
config.Site.storageSite               = 'T2_CH_CERN'#'T2_BE_IIHE' 


  
if __name__ == '__main__':

  import urllib, os, glob
  def download(url, destination):
    try:    os.makedirs(destination)
    except: pass
    urllib.urlretrieve(url, os.path.join(destination, url.split('/')[-1])) 

  def getSeedsForDoubleEle(year): # note: only getting DoubleEle seeds here
    prescalePage = 'https://tomc.web.cern.ch/tomc/triggerPrescales/%s/' % year
    hltTrigger   = 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL'
    dirToStore   = os.path.join('prescaleInformation', year, hltTrigger)
    download(prescalePage + hltTrigger + '.php', dirToStore) 
    with open(os.path.join(dirToStore, hltTrigger + '.php')) as f:
      for line in f:
        if 'prescale1' in line and 'L1_DoubleEG' in line: 
          download(prescalePage + line.split('>')[0].split('=')[-1], dirToStore)

    for json in glob.glob(os.path.join(dirToStore, '*.json')):
      leg1 = int(json.split('L1_DoubleEG_')[-1].split('_')[0].replace('LooseIso', ''))
      leg2 = int(json.split('L1_DoubleEG_')[-1].split('_')[1].replace('LooseIso', ''))
      yield leg1, leg2, json


  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  from httplib import HTTPException

  # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
  # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
  config.General.workArea = 'crab_%s' % submitVersion

  def submit(config, sample, name, leg1threshold, leg2threshold):
    config.General.requestName  = name + '_%s_%s' % (leg1threshold, leg2threshold)#sample.split('/')[-3] + '_%s_%s' % (leg1threshold, leg2threshold)
    config.Data.inputDataset    = sample
    config.Data.outLFNDirBase   = '%s/%s/' % (mainOutputDir,'mc')
    config.Data.splitting       = 'FileBased'
    #config.Data.lumiMask        = json
    config.Data.unitsPerJob     = 5
    config.JobType.pyCfgParams  = defaultArgs + ['L1Threshold=%s' % leg1threshold]
   
    try:
      crabCommand('submit', config = config)
    except HTTPException as hte:
      print "Failed submitting task: %s" % (hte.headers)
    except ClientException as cle:
      print "Failed submitting task: %s" % (cle)
    #print name + '_%s_%s' % (leg1threshold, leg2threshold)#sample.split('/')[-3] + '_%s_%s' % (leg1threshold, leg2threshold)
      
#leg1_thresh_list = [18, 22, 24, 25]
 
#for leg1 in leg1_thresh_list:
    # Crab fails on this on second iteration, of course with only a very cryptic error message
    # Not sure how to workaround this
  
submit(config, '/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM','DY1JetsToLL_M50_madgraphMLM', 25, 0)
submit(config, '/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_v3_94X_mc2017_realistic_v14_ext1-v2/MINIAODSIM','DY1JetsToLL_M50_madgraphMLM_ext', 25, 0)
submit(config, '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM', 'DYJetsToLL_M50_amcatnloFXFX',25, 0)
submit(config, '/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM','DYJetsToLL_M50_amcatnloFXFX_ext', 25, 0)
 





   
