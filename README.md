# Instructions to postprocess FMS history output on PP/AN

1. Clone postprocessing template repository

```
module load fre/canopy
fre pp checkout -e EXPNAME -p PLATFORM -t TARGET
```

2. Configure pp template with either XML or pp.yaml

```
fre pp convert -e EXPNAME -p PLATFORM -t TARGET -x XML

or

fre pp configure -e EXPNAME -p PLATFORM -t TARGET -y YAML
```

3. Validate the configuration

```
fre pp validate -e EXPNAME -p PLATFORM -t TARGET
```

4. Install the workflow

```
fre pp install -e EXPNAME -p PLATFORM -t TARGET
```

5. Run the workflow

```
fre pp run -e EXPNAME -p PLATFORM -t TARGET
```

6. Report status of workflow progress

```
fre pp status -e EXPNAME -p PLATFORM -t TARGET
```

7. Launch GUI

```
TODO: fre pp gui?

The full GUI can be launched on jhan or jhanbigmem (an107 or an201).

cylc gui --ip=`hostname -f` --port=`jhp 1` --no-browser
```
