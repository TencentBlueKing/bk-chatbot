<img src="docs/resource/img/bk-chatbot.png" alt="image" style="zoom: 80%;" />

# bk-chatbot

## Product Description

bk-chatbot is a BlueKing SaaS product that allows task configuration through a visual web interface and task execution through conversational interaction via chat terminal software such as WeChat Work robots.

bk-chatbot has two core services, one is the plug-in integration service: currently the default integration of the job platform and the sops(standard operation platform system), we will gradually open the user-defined plug-in service; the second is the intention understanding service: the user task configuration to collect the corpus, through NLP, similarity algorithms and other technologies trained into recognition models, user using the robot chat interaction, accurate matching to the task you need to run.

Using bk-chatbot, you can run job and sops tasks more easily and quickly, and you can also run tasks through WeChat Work on the cell phone when you are not at the computer.

## Overview

### Usage Scenarios

bk-chatbot is mainly used for operation task execution scenarios, such as version release, change, query and other execution-type operations; through the interaction of WeChat Work robot, it implement convenient and fast operation task execution without login to the community version of BlueKing; at the same time, it is very suitable for mobile office scenarios.

## Features

Plug-in support: support for the job and sops platform and other plug-in services in default, as the official standard plug-in services, but also supports user-defined plug-in development, custom development of standard plug-ins.

Chat terminal support: default support for WeChat Work robot service, but also support user-defined to join other terminal software such as QQ, slack and other bot services.

Interactable task execution: when initiating a session with the robot, the parameters of the task can be accessed interactively.

Generic permission management: implement the permission control of robot intention task skills by configuring the initiator role.

## Getting started

- [installation](docs/deploy.md)

## Usage

- [usage doc](docs/createskills.md)

## Roadmap

- [release log](docs/release.md)

## Support

- [bk forum](https://bk.tencent.com/s-mart/community/)

- [bk DevOps online video tutorial(In Chinese)](https://cloud.tencent.com/developer/edu/major-100008)

- Contact us, bk-chatbot technical communication QQ group: 639855706

  <img src="docs/resource/img/qq_group.png" alt="image" style="float:left;zoom: 50%;" />

## BlueKing Community

- [BK-CI](https://github.com/Tencent/bk-ci)：a continuous integration and continuous delivery system that can easily present your R & D process to you.
- [BK-BCS](https://github.com/Tencent/bk-bcs)：a basic container service platform which provides orchestration and management for micro-service business.
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas)：a SaaS provides users with highly scalable, flexible and easy-to-use container products and services.
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：an development platform that allows developers to create, develop, deploy and manage SaaS applications easily and quickly.
- [BK-SOPS](https://github.com/Tencent/bk-sops)：an lightweight scheduling SaaS for task flow scheduling and execution through a visual graphical interface.
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：an enterprise-level configuration management platform for assets and applications.

## Contributing

If you have good ideas or suggestions, please let us know by Issues or Pull Requests and contribute to the Blue Whale Open Source Community.

### License

```markdown
bk-chatbot is based on the MIT protocol. Please refer to [LICENSE](/LICENSE.txt).
```

