package v2

import (
	"dev.getsol.us/sources/common/Go/ypkg/shared"
	"gopkg.in/yaml.v3"
	"os"
)

// PackageDeps includes the dependencies required for the Build, Check, and Run Stages
type PackageDeps struct {
	Build []string      `yaml:"builddeps,omitempty"`
	Run   []interface{} `yaml:"rundeps,omitempty"`
}

// Convert turns a v2 PackageDeps into the intermediate "shared" PackageDeps
func (p PackageDeps) Convert() shared.PackageDeps {
	d := shared.NewPackageDeps()
	// Set build dependencies if not empty
	if len(p.Build) > 0 {
		d.Build[shared.BaseLabel] = p.Build
	}
	// Figure out rundeps for all sub-packages
	baseRun := make([]string, 0)
	// For each entry in the rundeps
	for _, r := range p.Run {
		switch v1 := r.(type) {
		case string:
			// strings get added to the base rundeps
			// e.g:
			// - one
			// - two
			// - three
			baseRun = append(baseRun, v1)
		case map[string][]interface{}:
			// maps contain lists of rundeps for the sub-packages
			// e.g:
			// - sub:
			//		- one
			//		- two
			//		- three
			for k, v2 := range v1 {
				part := make([]string, 0)
				for _, s := range v2 {
					part = append(part, s.(string))
				}
				d.Run[k] = part
			}
		default:
			// nothing else is allowed here
			panic(v1)
		}
	}
	// set base package rundeps if not empty
	if len(baseRun) > 0 {
		d.Run[shared.BaseLabel] = baseRun
	}
	return d
}

// BuildFlags are special options that configure the build process
type BuildFlags struct {
	AutoDep    bool     `yaml:"autodep,omitempty"`
	AVX2       bool     `yaml:"avx2,omitempty"`
	Clang      bool     `yaml:"clang,omitempty"`
	CCache     bool     `yaml:"ccache,omitempty"`
	Debug      bool     `yaml:"debug,omitempty"`
	Devel      bool     `yaml:"devel,omitempty"`
	Emul32     bool     `yaml:"emul32,omitempty"`
	Extract    bool     `yaml:"extract,omitempty"`
	LAStrip    bool     `yaml:"lastrip,omitempty"`
	Networking bool     `yaml:"networking,omitempty"`
	Optimize   []string `yaml:"optimize,omitempty"`
	Strip      bool     `yaml:"strip,omitempty"`
}

// Convert turns the v2 BuildFlags into the intermediate "shared" BuildFlags
func (f BuildFlags) Convert() shared.BuildFlags {
	fs := shared.BuildFlags{
		AutoDep:    f.AutoDep,
		AVX2:       f.AVX2,
		Clang:      f.Clang,
		CCache:     f.CCache,
		Debug:      f.Debug,
		Devel:      f.Devel,
		Emul32:     f.Emul32,
		Extract:    f.Extract,
		LAStrip:    f.LAStrip,
		Networking: f.Clang,
		Optimize:   f.Optimize,
		Strip:      f.Strip,
	}
	return fs
}

// BuildStages represent the scripted commands to execute for each stage of the build process
type BuildStages struct {
	Setup   string `yaml:"setup,omitempty"`
	Build   string `yaml:"build,omitempty"`
	Profile string `yaml:"profile,omitempty"`
	Check   string `yaml:"check,omitempty"`
	Install string `yaml:"install"`
}

// Convert turns a v2 BuildStages into the intermediate "shared" BuildStages
func (s BuildStages) Convert() shared.BuildStages {
	return shared.BuildStages{
		Setup:   s.Setup,
		Build:   s.Build,
		Profile: s.Profile,
		Check:   s.Check,
		Install: s.Install,
	}
}

// PackageYML is the v2 representation of the Package YML specification
type PackageYML struct {
	Name         string              `yaml:"name"`
	Version      string              `yaml:"version"`
	Release      uint                `yaml:"release"`
	Source       []map[string]string `yaml:"source"`
	Homepage     string              `yaml:"homepage,omitempty"`
	License      interface{}         `yaml:"license"`
	Component    interface{}         `yaml:"component"`
	Summary      interface{}         `yaml:"summary"`
	Description  interface{}         `yaml:"description"`
	Flags        BuildFlags          `yaml:"flags,omitempty,inline"`
	Dependencies PackageDeps         `yaml:"dependencies,inline,omitempty"`
	Environment  string              `yaml:"environment,omitempty"`
	Stages       BuildStages         `yaml:",inline"`
	Patterns     interface{}         `yaml:"patterns,omitempty"`
	f            *os.File
}

// ConvertDerps is a special function for converting non-standard YAML from v2 into fields
// used by the intermediate "shared" representation.
func ConvertDerps(derps interface{}) map[string][]string {
	// We are going to put everything into this format, even if it doesn't match
	less := make(map[string][]string)
	switch v := derps.(type) {
	case string:
		// all singular strings belong to the base package
		// e.g.:
		// Field: one
		less[shared.BaseLabel] = []string{v}
	case []interface{}:
		// Everything else is an array of something
		for _, e := range v {
			switch v2 := e.(type) {
			case string:
				// strings here belone to the base package
				// e.g.:
				// Field:
				//	- one
				//  - two
				//  - three
				less[shared.BaseLabel] = append(less[shared.BaseLabel], v2)
			case map[string]interface{}:
				// Fields here belong to sub-packages, but come in different flavors
				for k, v3 := range v2 {
					switch v4 := v3.(type) {
					case string:
						// e.g.:
						// Field:
						//	- sub: one
						less[k] = append(less[k], v4)
					case []interface{}:
						// e.g.:
						// Field:
						// 	- sub:
						//		- one
						//		- two
						for _, v5 := range v4 {
							switch v6 := v5.(type) {
							case string:
								less[k] = append(less[k], v6)
							default:
								panic(v6)
							}
						}
					default:
						// everything else is illegal
						panic(v4)
					}
				}
			default:
				// everything else is illegal
				panic(v2)
			}
		}
	case nil:
		// if nil, return the empty map
		return less
	default:
		// everything else is illegal
		panic(v)
	}
	return less
}

// Convert turns a v2 PackageYML into the intermediate "shared" Package representation
func (p PackageYML) Convert() shared.Package {
	return shared.Package{
		Name:         p.Name,
		Version:      p.Version,
		Release:      p.Release,
		Homepage:     p.Homepage,
		Source:       p.Source,
		License:      ConvertDerps(p.License),
		Component:    ConvertDerps(p.Component),
		Summary:      ConvertDerps(p.Summary),
		Description:  ConvertDerps(p.Description),
		Flags:        p.Flags.Convert(),
		Environment:  p.Environment,
		Dependencies: p.Dependencies.Convert(),
		Stages:       p.Stages.Convert(),
		Patterns:     ConvertDerps(p.Patterns),
	}
}

// Load populates a v2 PackageYML by reading in the contents from a specific filepath
func (p *PackageYML) Load(path string, mode int) error {
	// p.Flags = DefaultBuildFlags
	f, err := os.OpenFile(path, mode, 00644)
	if err != nil {
		return err
	}
	p.f = f
	dec := yaml.NewDecoder(p.f)
	return dec.Decode(p)
}

// Save writes any changes to this PackageYML to the currently open file descriptor
func (p *PackageYML) Save() error {
	// Seek to the beginning of the file
	_, err := p.f.Seek(0, 0)
	if err != nil {
		return err
	}
	// clear the contents of the file
	err = p.f.Truncate(0)
	if err != nil {
		return err
	}
	// write out the new contents to the file
	enc := yaml.NewEncoder(p.f)
	return enc.Encode(&p)
}

// Close close the file descriptor for this PackageYML
func (p *PackageYML) Close() {
	_ = p.f.Close()
}
