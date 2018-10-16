#SoftWAER firmware

This firmware is supposed to be runing on a BeagleBone Green wireless. Its perpose is to help you to connect and see sensors connected to the board through a simple interface for now.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For the firmeware to run you will need:
* Beaglebone Green wireless
* PC or Mac with Python 3 installed
* USB micro to A cable
* Micro SD card with a way to write it on the PC
* Sensors that you want to have on the board

### Installing

Download and falsh the "debian 8.10" image from the [Beaglebone image repo](https://beagleboard.org/latest-images). To flash it onto the board.

We the flash is done, plug your beaglebone to a PC and access it with SSH (ssh debian@192.168.7.2 by default).

Connect the board to a accessible network (with only a password and not a username/password combo) by following this:


A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
