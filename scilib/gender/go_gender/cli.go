package main

import (
	"fmt"
	"os"
	"strconv"

	c "github.com/hstove/gender/classifier"
)

func main() {
	var classifier = c.Classifier()

	for i := 1; i < len(os.Args); i++ {
		name := os.Args[i]
		gender, prob := c.Classify(classifier, name)
		prob = prob * 100
		probability := strconv.FormatFloat(prob, 'f', 6, 64)
		fmt.Printf("%s,%s,%s\n", name, gender, probability)
	}
}
