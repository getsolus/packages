package cli

import (
	"github.com/DataDrake/cli-ng/cmd"
)

var Root = cmd.Root{
	Name:   "ypkg-tools",
	Short:  "various tools for manipulating ypkg build files",
	Flags:  &RootFlags{},
	Single: false,
}

type RootFlags struct{}
