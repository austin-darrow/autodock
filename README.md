This application runs AutoDock Vina virtual screening using the user's protein receptor and a selected ligand library on the [Texas Advanced Computing Center (TACC)](https://www.tacc.utexas.edu/) [Lonestar6 supercomputer](https://www.tacc.utexas.edu/systems/lonestar6). Utilizing Python's [mpi4py](https://mpi4py.readthedocs.io/en/stable/) library, the application allows the user to submit batch jobs that dock up to thousands of molecules in parallel.

Note: Computer docking and virtual screening are inexact, but potentially very valuable, tools. This site is intended to provide easy access to researchers wishing to perform small numbers of docking or virtual screening experiments, but who do not have the necessary computer resources and/or computational biology backgrounds. This interface can handle most protein-ligand docking experiments, but there will always be systems where this simple interface will fail. For those cases, researchers will need to develop the necessary expertise or collaborations to perform the experiment.



 Running the Application:
-----------------------

To run the application, the user must submit a job using the [TACC API (TAPIS) UTRC Portal system](https://utrc.tacc.utexas.edu/). The following inputs are allowed:
- __Protein Receptor__: The user _must_ upload a .pdb- or .pdbqt-formatted protein receptor file
- __Grid Center__: The user _may_ specify X-Y-Z coordinates; default is x: 15.190, y: 53.903, z: 16.917
- __Box Size__: The user _may_ specify X-Y-Z size limits; default is 20-20-20
- __Scoring Method__: The user _must_ specify which scoring method to use (either AutoDock Vina or AutoDock4); default is Vina. More details on the differences can be found [here](https://autodock-vina.readthedocs.io/en/latest/faq.html)
- __Docking Type__: The user _must_ specify whether this is basic or flexible docking; default is basic
- __Flex Residues__: If Flexible Docking is chosen, the user _must_ specify the specific flexible residues (e.g. THR315)
- __Ligand Library__: The user _must_ choose one of the ligand libraries to run this virtual screening on


 Output Visualization:
---------------------

The user may also choose to visualize their resulting output file utilizing the [ChimeraX application](https://github.com/tiffanyhuff/ChimeraXApp) on the [Texas Advanced Computing Center (TACC)](https://www.tacc.utexas.edu/) [Lonestar6 supercomputer](https://www.tacc.utexas.edu/systems/lonestar6). To run the application, the user must submit a job using the [University of Texas Research Cyberinfrastructure (UTRC) system](https://utrc.tacc.utexas.edu/). A virtual DCV session will be initialized for the user, and a document titled 'ChimeraX_dcvserver.txt' will be created in the user's work folder with connection instructions. Once connected, the [University of California San Francisco (UCSF)](https://www.ucsf.edu/) [ChimeraX](https://www.cgl.ucsf.edu/chimerax/) software will begin running, and a Tapis jobs archive folder will be created on the desktop for the user's convenience. The user may then use the ChimeraX program to open the file containing the top scoring docked ligands.

 Docking Software:
---------------------

[AutoDock Vina](http://vina.scripps.edu/), written by Drs. O. Trott and A. Olson at the Scripps Institute is used to perform the actual docking. This open-source program has been made freely available by the authors.

[AutoDockTools](http://autodock.scripps.edu/resources/adt/index_html/), written by Drs. G. Morris and A. Olson at the Scripps Institute is used to convert proteins and ligands to the format required by AutoDock Vina. This open-source program has been made freely available by the authors.

[J. Eberhardt, D. Santos-Martins, A. F. Tillack, and S. Forli. (2021). AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. Journal of Chemical Information and Modeling.](https://pubs.acs.org/doi/10.1021/acs.jcim.1c00203)

[O. Trott and A. J. Olson. (2010). AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of computational chemistry, 31(2), 455-461.](https://onlinelibrary.wiley.com/doi/10.1002/jcc.21334)

ChimeraX Software:
---------------------

Molecular graphics and analyses performed with UCSF ChimeraX, developed by the Resource for Biocomputing, Visualization, and Informatics at the University of California, San Francisco, with support from National Institutes of Health R01-GM129325 and the Office of Cyber Infrastructure and Computational Biology, National Institute of Allergy and Infectious Diseases.

[UCSF ChimeraX: Structure visualization for researchers, educators, and developers. Pettersen EF, Goddard TD, Huang CC, Meng EC, Couch GS, Croll TI, Morris JH, Ferrin TE. Protein Sci. 2021 Jan;30(1):70-82.](https://pubmed.ncbi.nlm.nih.gov/32881101/)

[UCSF ChimeraX: Meeting modern challenges in visualization and analysis. Goddard TD, Huang CC, Meng EC, Pettersen EF, Couch GS, Morris JH, Ferrin TE. Protein Sci. 2018 Jan;27(1):14-25.](https://pubmed.ncbi.nlm.nih.gov/28710774/)