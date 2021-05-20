from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from . import models
# from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import auth

from django.db.models import Q
# Create your views here.

# 注册的视图函数
from . import forms


def registe(request):
    if request.method == "POST":
        # form_obj = forms.reg_form(request.POST)#有图片上传,这个句代码是错误的!!!!!!!!!!!
        form_obj = forms.reg_form(request.POST, request.FILES)

        if form_obj.is_valid():  # 判断校验是否通过
            form_obj.cleaned_data.pop("repassword")
            # head_img = request.FILES.get("head_img")
            user_obj = models.loguser.objects.create_user(**form_obj.cleaned_data, is_staff=1, is_superuser=1)
            # obj.is_staff
            auth.login(request, user_obj)  # 用户登录，可将登录用户赋值给request.user
            return redirect('/')
        else:
            # print(form_obj['repassword'].errors)
            return render(request, "blog/registe.html", {"formobj": form_obj})
    form_obj = forms.reg_form()  # 生成一个form对象
    return render(request, "blog/registe.html", {"formobj": form_obj})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")  # 从提交过来的数据提取用户名和密码
        pwd = request.POST.get("password")
        user = auth.authenticate(username=username, password=pwd)  # 利用auth模块做用户名和密码的校验
        # print(type(user),user)
        if user:
            auth.login(request, user)  # 用户登录，并将登录用户赋值给request.user
            return redirect("/")
        else:
            errormsg = "用户名或密码错误！"
            return render(request, 'blog/login.html', {'error': errormsg})
    return render(request, 'blog/login.html')


class blogdetailview(DetailView):
    model = models.Blog
    template_name = 'blog/detail.html'
    context_object_name = 'blog'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        blog = super(blogdetailview, self).get_object(queryset=None)
        blog.increase_views()
        return blog

    def get_context_data(self, **kwargs):
        context = super(blogdetailview, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


class categoryview(ListView):
    model = models.Blog
    template_name = 'blog/index.html'
    context_object_name = 'blog_list'

    def get_queryset(self):
        cate = get_object_or_404(models.Category, pk=self.kwargs.get('pk'))
        return super(categoryview, self).get_queryset().filter(category=cate).order_by('-created_time')
