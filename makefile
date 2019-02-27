all: conda

clean:
	python setup.py clean

dev:
	python setup.py develop

conda:
	rm -rf conda_build
	conda build --output-folder conda_build -n .
	#conda convert --platform all conda_build/linux-64/*.tar.bz2 -o conda_build/
	anaconda upload --force -u coml conda_build/*/*.tar.bz2
