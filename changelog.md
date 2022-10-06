# v0.3.0
- 工程比较，典型应用场景：
1. 修包：修复在 2203中构建成功，但是2209工程中构建失败的包——》输出哪些包2203成功，但是2209失败
2. 对比：同一个工程，不同的仓库下的构建差异。Java工程 2203仓库和2209仓库没有构建成功的包对比
3. 进展观察：同一个工程，同一个仓库，上个月和这个月的差异，哪些包原来失败，现在成功


- 新增ObservatoryPackages.py文件，将原本的misc.py文件中的包搜索功能代码移入该文件，添加相似工程差异比较方面代码。

  - 新增两个页面的功能分别从时间（Temporal）和空间（Spatial）两个维度对相似工程进行比较。
  - 时间维度，比较单个仓库在不同时间的差异。

    - 为了实现这个功能，我将之前比较项目的统计数据差异的代码提取成匹配函数match_ordered、match_unordered和一个类Differ，存放于Utils.py文件中。
    - 通过改变Differ的成员变量，例如commit id和path，即可实现不同数据格式、不同路径下文件的差异比较，使得Differ类的差异比较功能具有较高泛用性。
    - match_ordered函数对有序数据进行差异比较，使用的方法是循环遍历。
    - match_unordered函数对无序数据进行差异比较，使用hash和集合(交集，差集)的方法切割数据。
  
  - 空间维度，比较最新数据下两个不同仓库的差异。差异比较方法用的是match_unordered

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