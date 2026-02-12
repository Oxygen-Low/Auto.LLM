# Auto.LLM
Allow an LLM to completely access a computer, by itself.

Note:
We recommend you run this in Docker, on a virtual machine, on a closed/private network, and ensure that you watch what the LLM is doing closely for security.

This was originally designed to be an experiment to see what would LLMs do if they owned an entire computer.

It contains a server, which contains custom, and non-custom locally hostable tools for the LLMs to interact with including:

- Github
- Storage
- User Registration (I recommend you create the LLM's accounts first, then give them the login info on their desktops) (the user registration is used for the other tools)
- Credits (a simple credit system that allows LLMs to see where they spent their credits and what on (credits are the currency they can earn, and spend on other tools))

You can also run your own tools by running them on Docker, then informing the LLMs on which port it is located on.
