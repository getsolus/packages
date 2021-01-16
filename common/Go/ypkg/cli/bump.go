package cli

import (
	"fmt"
	"github.com/DataDrake/cli-ng/cmd"
	"os"
	"path/filepath"
	ypkg "dev.getsol.us/sources/common/Go/ypkg/v2"
)

var Bump = cmd.Sub{
	Name:  "bump",
	Alias: "bump",
	Short: "Bump will increment the release number for the package.yml in the current working directory",
	Flags: &BumpFlags{},
	Args:  &BumpArgs{},
	Run:   RunBump,
}

func init() {
	cmd.Register(&Bump)
}

type BumpArgs struct{}
type BumpFlags struct{}

func RunBump(r *cmd.Root, c *cmd.Sub) {
	workDir, _ := os.Getwd() // Get the current work directory
	ymlPath := filepath.Join(workDir, "package.yml")

	var yml ypkg.PackageYML // Create our new PackageYml struct
	if loadErr := yml.Load(ymlPath, os.O_RDWR); loadErr != nil {
		fmt.Printf("failed to load our package.yml: %s\n", loadErr)
		os.Exit(1)
	}

	yml.Release++                              // Bump
	if saveErr := yml.Save(); saveErr != nil { // Failed to save the file
		fmt.Printf("failed to save our package.yml: %s\n", saveErr)
		os.Exit(1)
	}
}
