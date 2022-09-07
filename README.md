# data-center
## usage
python需要提前安装Flask和pandas，同时python版本建议3.6及以上，直接运行下面的命令即可执行后端
- python obs_observatory.py

## 注意事项
我修改了oerv_script/script/main.py的部分代码，使其具备自动上传功能.
部署时后端，必须配置好git环境，确保和gitee和oerv_obsdata仓库关联.
- 需要说明的是，本项目是github中的仓库，而oerv_obsdata则是gitee中的仓库，因此，在部署时需要首先生成ssh key并置于github与gitee各自setting中，详见：https://todebug.com/tips/
- 记得修改oerv_script/script/constant.py中的信息