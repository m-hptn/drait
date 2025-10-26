// Configuration script for docToolchain

outputPath = 'build'

// Path where the docToolchain will search for input files.
inputPath = 'src/docs'

// These are directories included in the input path.
inputFiles = [
    [file: 'arc42.adoc', formats: ['html','pdf','docbook']],
]

taskInputsDirs = [
    "${inputPath}",
    "${inputPath}/chapters",
]

taskInputsFiles = []

confluence = [:]
