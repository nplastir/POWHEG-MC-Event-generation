# Instructions for the ttb-jets MC event production with POWHEG-BOX-RES

## Setup

All commands are given relative to a `$base` (set it e.g. via `base=$PWD` in your desired installation directory)

Set up a CMSSW_10_2_14 environment:
```
cd $base
scram project CMSSW_10_2_14
cd $base/CMSSW_10_2_14/src
cmsenv
cd $base
```
Install `yaml` package for python3:
```
pip3 install --user pyyaml
```

Install POWHEG-BOX-RES:
```
cd $base
svn checkout --revision 3604 --username anonymous --password anonymous svn://powhegbox.mib.infn.it/trunk/POWHEG-BOX-RES
```
We are using revision 3604, which is the stable release version. More recent revisions have not been tested yet.

Get the code for the ttbb process:
```
cd $base/POWHEG-BOX-RES
git clone ssh://git@gitlab.cern.ch:7999/tjezo/powheg-box-res_ttbb.git ttbb
```
Enter the ttbb directory and check out the appropriate commit that fits to r3604 of the POWHEG-BOX-RES code:
```
cd $base/POWHEG-BOX-RES/ttbb
git checkout 128aefb6061b72714d34e5f1d4798967f76f9585
```
Then compile the fortran code of POWHEG:
```
cd $base/POWHEG-BOX-RES/ttbb
make pwhg_main
make lhef_decay
```

The ttbb POWHEG code is now in principle ready to run. We can now also install this repository to ease the event generation and submit to HTCondor:
```
cd $base
git clone git@github.com:JanvanderLinden/POWHEG-MC-Event-generation.git
```

For a new production it is recommended to create a new directory now in which you can store everything needed for that production, e.g.
```
cd $base
mkdir production_test
cd production_test
production=$PWD
```

In `$base/POWHEG-MC-Event-generation/ttbb_powheg_inputs/` a few `powheg.input` files are stored which can be used as examples for event production. The settings of course can be adjusted based on what configuration is supposed to be generated.

## Setting up a run

In `POWHEG-MC-Event-generation` three stages are supported for running all of the powheg parallel stages. 
To start a run from scratch, first an intialization has to be performed where a working directory is created and settings are determined.
Then, parallelstages can be run (i.e. submitted to HTCondor).
After one stage has finished, the output of the previous stage can be validated.

### Initialization

Initialize a new run via:
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py --init -p ../POWHEG-BOX-RES/ttbb -i ../POWHEG-MC-Event-generation/ttbb_powheg_inputs/powheg.input_nominal -t test
```
Use the help function of `POWHEG-MC-Event-generation/run.py` for more details on the options.
In summary, with `-p` the path to the process directory in your `POWHEG-BOX-RES` has to be given, `-i` specifies a `powheg.input` file to use for this production and `-t` specifies a name tag for the run to differentiate it from other productions.
In addition, factors for renormaliation scale (`--mur`), factorization scale (`--muf`), pdf set (`--pdf`), top mass (`--mass`) can be changed in this initialization step. The default values are `--muf 1.0 --mur 1.0 --pdf 320900 --mass 172.5`.

### Running a parallel stage

After initialization of the run parallel stages can be submitted, e.g. start a full production with
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 1 -n [NBATCHES]
```
Here, `-w` specifies the path to the previously created workdirectory (so for the specific example above it would be `-w ./test__r1.0_f1.0_m172.5_p320900`). With `-n` you can create the number of jobs to be submitted, e.g. `-n 1000` for 1000 submitted jobs.
The parameters `-S` and `-X` specify the parallel stage (`-S`) and xgriditeration (`-X`) to run. For more details on the parallel stages see below.

### Validating

After the jobs of one parallel stage are done the output can be validated before the next stage has to be run:
```

cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 1 -n [NBATCHES] --validate
```
If validation was successful the next stage can be run.


## LHE file production

Parallel stages 1-3 are for preparation of integration grids, so if the inputs for producing LHE files are already available only stage 4 has to be run.
For this purpose, first initialize a working directory with the appropriate generator settings (mur,muf,pdf,mass), and pick the appropriate `powheg.input` and `pwg-rwl` files. For simplicity you can also copy the already existing file
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/configs_nominal/powheg.input_muR1.0_muF1.0 $production/test__r1.0_f1.0_m172.5_p320900/powheg.input
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/configs_nominal/pwg-rwl.dat_320900 $production/test__r1.0_f1.0_m172.5_p320900/pwg-rwl.dat
```
Then, proceed to copy the grid files for the LHE run to the run directory in `POWHEG-BOX-RES/ttbb/` (e.g. with the initialization from the example above this would be `$base/POWHEG-BOX-RES/ttbb/run__test__r1.0_f1.0_m172.5_p320900`.
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_nominal/muR1.0_muF1.0/* $base/POWHEG-BOX-RES/ttbb/run__test__r1.0_f1.0_m172.5_p320900/
```
Jobs for LHE production can then be submitted via
```
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 4 -n [NBATCHES] -N [NEVTSPERJOB] --decay [DECAYCHANNEL] --force 
```
You have to append the option `--force` to force the submission of batch jobs as otherwise this is blocked as parallel stages 1-3 were skipped.
Two additional options are required for this step, `-N` and `--decay`. The first specifies the number of events per job (defaults to 1000), and the second specifies the ttbar decay channel.
This option is mandatory and has to be specified. The options are:
- `1L`: for semileptonic ttbar decays
- `0L`: for fully hadronic ttbar decays
- `2L`: for dileptonic ttbar decays
- `incl`: for inclusive ttbar decays

# POWHEG parallel stages
If **POWHEG** is run in parallel mode, there are 4 parallel stages in the generation process, where each has to be finished, before the next stage is started.

## Parallel stage 1
For this stage at least three iterations (steered via `xgriditeration` in powheg, and `-X` in the submit of jobs) are recommended.

## Parallel stage 2

## Parallel stage 3

## Parallel stage 4
In this step LHE files are produced.
