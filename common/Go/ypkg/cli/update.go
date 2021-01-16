package cli

import (
	"fmt"
	"github.com/DataDrake/cli-ng/cmd"
	"os"
	"path/filepath"
	shared "dev.getsol.us/sources/common/Go/ypkg/shared"
	"strconv"
	ypkg "dev.getsol.us/sources/common/Go/ypkg/v2"
)

var Update = cmd.Sub{
	Name:  "update",
	Alias: "update",
	Short: "Update will update the package.yml in the current directory to the given version and source",
	Flags: &UpdateFlags{},
	Args:  &UpdateArgs{},
	Run:   RunUpdate,
}

func init() {
	cmd.Register(&Update)
}

type UpdateArgs struct {
	Version string `desc:"Version of the package"`
	URL     string `desc:"URL to the source"`
}

type UpdateFlags struct {
	Position string `short:"pos" long:"position" desc:"Numerical position of the source we're updating. Starts at zero."`
}

func RunUpdate(r *cmd.Root, c *cmd.Sub) {
	args := c.Args.(*UpdateArgs)
	flags := c.Flags.(*UpdateFlags)

	if args.Version == "" { // No version provided
		fmt.Printf("no version provided\n")
		os.Exit(1)
	}

	if args.URL == "" { // No source provided
		fmt.Printf("no URL to the source provided\n")
		os.Exit(1)
	}

	workDir, _ := os.Getwd() // Get the current work directory
	ymlPath := filepath.Join(workDir, "package.yml")

	var yml ypkg.PackageYML // Create our new PackageYml struct
	if loadErr := yml.Load(ymlPath, os.O_RDWR); loadErr != nil {
		fmt.Printf("failed to load our package.yml: %s\n", loadErr)
		os.Exit(1)
	}

	sum, err := shared.HashSource(args.URL) // Download the file

	if err != nil {
		fmt.Printf("failed to download source: %s", err)
		os.Exit(1)
	}

	yml.Version = args.Version // Update the version

	var realPos int
	if flags.Position != "" { // Have a position
		realPos, _ = strconv.Atoi(flags.Position) // Convert our string position to an int
	}

	sourceMap := map[string]string{ // Update the source at this position
		args.URL: sum,
	}

	if realPos >= len(yml.Source) { // Greater than our length
		yml.Source = append(yml.Source, sourceMap)
	} else {
		yml.Source[realPos] = sourceMap
	}

	yml.Release++ // Bump while we're at it

	if saveErr := yml.Save(); saveErr != nil { // Failed to save the file
		fmt.Printf("failed to save our package.yml: %s\n", saveErr)
		os.Exit(1)
	}
}