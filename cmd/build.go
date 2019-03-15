package cmd

import (
    "github.com/spf13/cobra"
    "github.com/seveirbian/gear/build"
    "github.com/sirupsen/logrus"
)

var logger = logrus.WithField("cmd", "build")

var buildUsage = `Usage:  gear build IMAGENAME:TAG`

func init() {
    rootCmd.AddCommand(buildCmd)
    buildCmd.SetUsageTemplate(buildUsage)
}   

var buildCmd = &cobra.Command{
    Use:   "build",
    Short: "Build a gear image from a docker image",
    Long:  `Build a gear image from a docker image`,
    Args:  cobra.ExactArgs(1),
    Run: func(cmd *cobra.Command, args []string) {
        builder, err := build.InitBuilder(args[0])
        if err != nil {
            logger.Fatal("Fail to init a builder to build gear image...")
        }

        err = builder.Build()
        if err != nil {
            logger.Fatal("Fail to build gear image...")
        }
    },
}