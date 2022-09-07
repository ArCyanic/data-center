# v0.2.0
- 后端从Django向Flask迁移
  
  考虑Django文件组织较为复杂，而且有大多数功能是用不上的，因此向更为轻便的Flask迁移，以期提高开发效率。
- flask app模块化

  原先的代码将所有的接口都放在一个文件中，不利于后续维护，因此通过flask的Blueprint重新组织文件，将网页上不同的Section所对应的接口划分到不同的app中。

- 优化数据更新逻辑，便于部署

  原先数据的更新只有中间文件更新，而且git pull操作散落在各个接口中，对于部署显然是不合理的。因此本次将所有和数据更新有关的git操作集中到一个函数Update.py文件的updateLocal中，再额外添加一个用于更新oerv_obsdata仓库的函数updateRepository，从而将数据更新操作集中的一个文件中进行管理。

- 更新oerv_obsdata

  Update.py中的updateRepository函数可以实现oerv_obsdata仓库的更新，实现步骤如下：
  - 将[爬取数据的仓库](https://gitee.com/phoebe-xi/oerv_script/tree/master/obs)克隆到本项目中
  - 克隆oerv_obsdata仓库到该文件夹下，并[用ssh关联到gitee](https://todebug.com/tips/)
  - 修改constant.py文件
  - 修改main.py文件dataPath(相对路径从'../..'修改成'../')
  - 在main.py文件中用os.system函数进行数据的上传。
  
  该函数在执行时首先会pull拉取数据，然后再执行抓取数据的脚本。

- Package搜索功能

  主要通过OBS API实现，调用search API，获得返回的网页，用正则表达式过滤出包和路径即可。

- 可视化图表的数据处理

  本次添加的两个图表的处理都相对枯燥繁琐，并无特殊之处。