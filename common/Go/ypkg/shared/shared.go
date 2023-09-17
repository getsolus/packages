package shared

// BaseLabel is the string key used for values related to the base package
const BaseLabel = "*"

// PackageDeps includes the dependencies required for the Build, Check, and Run Stages
type PackageDeps struct {
	Build map[string][]string
	Check map[string][]string
	Run   map[string][]string
}

// NewPackageDeps returns an empty PackageDeps, with properly initialized maps
func NewPackageDeps() PackageDeps {
	return PackageDeps{
		Build: make(map[string][]string),
		Check: make(map[string][]string),
		Run:   make(map[string][]string),
	}
}

// BuildFlags are special options that configure the build process
type BuildFlags struct {
	AutoDep    bool
	AVX2       bool
	Clang      bool
	CCache     bool
	Debug      bool
	Devel      bool
	Emul32     bool
	Extract    bool
	LAStrip    bool
	Networking bool
	Optimize   []string
	Strip      bool
}

// DefaultBuildFlags represents the default values for all build flags, unless overwritten
var DefaultBuildFlags = BuildFlags{
	AutoDep:    true,
	AVX2:       false,
	CCache:     true,
	Clang:      false,
	Debug:      true,
	Devel:      false,
	Emul32:     false,
	Extract:    true,
	LAStrip:    true,
	Networking: false,
	Strip:      true,
}

// BuildStages represent the scripted commands to execute for each stage of the build process
type BuildStages struct {
	Setup   string
	Build   string
	Profile string
	Check   string
	Install string
}

// Package is the intermediate representation of all formats of the Package YML specification
type Package struct {
	Name         string
	Version      string
	Release      uint
	Source       []map[string]string
	Homepage     string
	License      map[string][]string
	Component    map[string][]string
	Summary      map[string][]string
	Description  map[string][]string
	Flags        BuildFlags
	Environment  string
	Dependencies PackageDeps
	Stages       BuildStages
	Patterns     map[string][]string
}
