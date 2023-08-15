package main

import (
	"bufio"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"os/user"
	"path/filepath"
	"strings"
)

// PausePrompt will prompt the user if the directory is correct and exit if it is not
func PausePrompt() {
	var response string
	var yesNo bool

	for !yesNo { // While we haven't replied yes / no
		fmt.Print("Does this directory contain all the child directories of various repos (such as nano)? [y/N]: ")
		stdinReader := bufio.NewReader(os.Stdin)     // Create a new buffer IO reader that reads stdinReader
		input, _ := stdinReader.ReadString('\n')     // Read anything before a new line
		input = strings.Replace(input, "\n", "", -1) // Remove any new lines
		loweredInput := strings.ToLower(input)

		yesNo = ((loweredInput == "y") || (loweredInput == "n"))

		if yesNo {
			response = loweredInput
			break
		}
	}

	if response != "y" {
		fmt.Println("Please run in the correct directory. Exiting.")
		os.Exit(1)
	}
}

func main() {
	fmt.Println("This script will attempt to update all your git URLs for repos to point to github.com/solus-packages.")
	fmt.Println("In the event this is not successful, please reclone common and re-run make clone.")
	PausePrompt()

	// If we're continuing, we're in the right directory
	workDir, getWdErr := os.Getwd();
	if getWdErr != nil {
		fmt.Println("Failed to determine the current working directory. Exiting.")
		os.Exit(1)
	}

	failedRepoChanges := []string{}
	currentUser, getUserErr := user.Current() // Get the current user

	if getUserErr != nil { // If we failed to get the current user
		fmt.Println("Failed to determine the current user. Exiting.")
		os.Exit(1)
	}

	workDir = strings.Replace(workDir, "~", currentUser.HomeDir, -1)
	fmt.Printf("Determined full working directory path to be: %s\n", workDir)

	dir, dirOpenErr := os.Open(workDir) // Attempt to open this directory
	if dirOpenErr != nil {
		fmt.Printf("Failed to open this directory for reading. Exiting with %s\n", dirOpenErr.Error())
		os.Exit(1)
	}

	dirNames, dirReadErr := dir.Readdirnames(-1) // Get all the directory names
	if dirReadErr != nil {
		fmt.Printf("Failed to read the contents of this directory. Exiting with %s\n", dirReadErr.Error())
	}

	counter := 0
	for _, dir := range dirNames { // For each directory

		// These live on getsolus github org
		if dir == "common" || dir == "infrastructure-tooling" {
			continue
		}

		repoPath := filepath.Join(workDir, dir)
		repoGitConfigPath := filepath.Join(repoPath, ".git", "config") // Combine the paths to get to .git/config

		repoFile, repoOpenErr := os.Open(repoPath) // Read the path so we can determine if it is a directory or file
		if repoOpenErr != nil {
			fmt.Printf("Failed to open %s", repoPath)
			failedRepoChanges = append(failedRepoChanges, dir)
			continue
		}

		repoStats, repoStatErr := repoFile.Stat() // Get the stats
		if repoStatErr != nil {
			fmt.Printf("Failed to stat %s. Adding to a report at the end.", repoFile.Name())
			failedRepoChanges = append(failedRepoChanges, dir)
			continue
		}
		if !repoStats.IsDir() {
			fmt.Printf("%s isn't a directory, skipping.\n", repoStats.Name())
			continue
		}

		if _, err := os.Stat(repoGitConfigPath); errors.Is(err, os.ErrNotExist) {
			fmt.Printf("%s isn't a git repository, skipping.\n", repoGitConfigPath)
			continue
		}

		fmt.Printf("Attempting to read: %s\n", repoGitConfigPath)
		configContents, configReadErr := os.ReadFile(repoGitConfigPath)
		if configReadErr != nil {
			fmt.Printf("Failed to read %s. Adding to a report at the end.\n", repoGitConfigPath)
			failedRepoChanges = append(failedRepoChanges, dir)
			continue
		}

		fmt.Printf("\033[35mAttempting to update: %s\033[0m\n", dir)
		config := string(configContents[:])                                                                  // Convert to a string
		config = strings.Replace(config, "http://dev.getsol.us/source/", "https://github.com/solus-packages/", -1)  // Replace HTTP with HTTPS
		config = strings.Replace(config, "https://dev.getsol.us/source/", "https://github.com/solus-packages/", -1) // Replace HTTPS
		config = strings.Replace(config, "ssh://vcs@dev.getsol.us:2222/source/", "git@github.com:solus-packages/", -1) // Replace SSH
		writeErr := ioutil.WriteFile(repoGitConfigPath, []byte(config), 0644)
		if writeErr != nil {
			fmt.Println("Failed to write the config. Adding to a report at the end.")
			failedRepoChanges = append(failedRepoChanges, dir)
		}
		counter += 1
	}

	if len(failedRepoChanges) > 0 { // If we failed to update some repos
		fmt.Println("List of failed repo updates:")
		for _, repo := range failedRepoChanges {
			fmt.Println(repo)
		}
	} else {
		fmt.Printf("\033[32mSuccessfully updated %d repos\033[0m\n", counter)
	}
}
