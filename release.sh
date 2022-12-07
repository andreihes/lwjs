  - name: Build package
      run: python -m build
    - name: Publish package
      run: |
        (
          echo __token__
          echo ${{ secrets.PYPI_API_TOKEN }}
        ) | python -m twine upload --repository testpypi dist/*
        