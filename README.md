This application runs AutoDock Vina virtual screening using the user's protein receptor and a selected ligand library on the [Texas Advanced Computing Center (TACC)](https://www.tacc.utexas.edu/) [Lonestar6 supercomputer](https://www.tacc.utexas.edu/systems/lonestar6). Utilizing Python's [mpi4py](https://mpi4py.readthedocs.io/en/stable/) library, the application allows the user to submit batch jobs that dock up to thousands of molecules in parallel.

Note: Computer docking and virtual screening are inexact, but potentially very valuable, tools. This site is intended to provide easy access to researchers wishing to perform small numbers of docking or virtual screening experiments, but who do not have the necessary computer resources and/or computational biology backgrounds. This interface can handle most protein-ligand docking experiments, but there will always be systems where this simple interface will fail. For those cases, researchers will need to develop the necessary expertise or collaborations to perform the experiment.



 Running the application:
-----------------------

To run the application, the user must submit a job using the [TACC API (TAPIS) Portal system](). The following inputs are allowed:
- __Protein Receptor__: The user _must_ upload a .pdb- or .pdbqt-formatted protein receptor file
- __Grid Center__: The user _may_ specify X-Y-Z coordinates; default is x: 15.190, y: 53.903, z: 16.917
- __Box Size__: The user _may_ specify X-Y-Z size limits; default is 20-20-20
- __Scoring Method__: The user _must_ specify which scoring method to use (either AutoDock Vina or AutoDock4); default is Vina. More details on the differences can be found [here](https://autodock-vina.readthedocs.io/en/latest/faq.html)
- __Docking Type__: The user _must_ specify whether this is basic or flexible docking; default is basic
- __Flex Residues__: If Flexible Docking is chosen, the user _must_ specify the specific flexible residues (e.g. THR315)
- __Ligand Library__: The user _must_ choose one of the ligand libraries to run this virtual screening on



 Docking software:
---------------------

[Autodock Vina](http://vina.scripps.edu/)\[1], written by Drs. O. Trott and A. Olson at the Scripps Institute is used to perform the actual docking. This open-source program has been made freely available by the authors.

[AutodockTools](http://autodock.scripps.edu/resources/adt/index_html/), written by Drs. G. Morris and A. Olson at the Scripps Institute is used to convert proteins and ligands to the format required by AutoDock Vina. This open-source program has been made freely available by the authors.

[1] "AutoDock Vina: Improving the Speed and Accuracy of Docking with a New Scoring Function, Efficient Optimization and Multithreading", (2010) O. Trott and A. J. Olson, J. Comp. Chem. 31, 455-461.


