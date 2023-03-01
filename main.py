from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.transition import MDSlideTransition
from kivymd.toast import toast
from json import dump,load
from numparser import NumParser as NP
import re

# importing font for math expressions
LabelBase.register(
	name="DejaVu",
	fn_regular="DejaVuSansCondensed.ttf"
)

# Main Class
class MainBaseApp(MDApp):
	# method to make dropdown menus
	def make_dropdown(self,names,funcs,caller):
		items = [{"viewclass":"OneLineListItem","text": i,"halign": "center","height": dp(54),"on_release": j}for i,j in zip(names,funcs)]
		menu = MDDropdownMenu(
			caller=caller,
			items=items,
			width_mult=2.5,
			max_height=dp(200))
		return menu
	# method to switch themes
## TODO: add this (full) to settings screen
	def decide_colors(self,style):
		if style == "Dark":
			res = ["Dark","DeepOrange","#070707","#bcbcbc","#a3a3a380","#f0f0f080"]
		else:
			res = ["Light","Green","#e0e0e0","#303030","#363636","#07070780"]
		return res
	# method to reset converter screens 
	# (is needed)
	# this may go on settings as :
	#Switch: Keep result from different conversions
	def init_convers(self,which,r):
		self.root.ids.my_toolbar.opacity = 0
		self.root.ids.my_toolbar.disabled = True
		self.current = self.convs[which]
		self.screen.ids.convy_label.text = self.cwords[r]
		a = [i for i in self.current.keys()]
		self.screen.ids.first.text = a[0]
		self.screen.ids.second.text = a[0]
		self.screen.ids.input_label.text = "0"
		self.screen.ids.output_label.text = "0"
		
		self.first_menu = self.make_dropdown(
			self.current.keys(),
			[lambda x=i:self.change_label(x,1)for i in self.current],
			self.screen.ids.first
		)
		self.second_menu = self.make_dropdown(
			self.current.keys(),
			[lambda x=i:self.change_label(x,0)for i in self.current],
			self.screen.ids.second
		)
	# method to change a widget's disability
	# USED ONLY FOR THE `MAIN_SCR`
	def disable(self,which):
		c = self.screen.ids.main_scr
		if which=='layer':
			if self.main_switched:
				c.remove_widget(self.scl)
				c.add_widget(self.mcl)
				self.main_switched = False
			else:
				c.remove_widget(self.mcl)
				c.add_widget(self.scl)
				self.main_switched = True
		elif which=='buttons':
			a = [[self.sin,self.cos,self.tan],[self.asin,self.acos,self.atan]]
			b = self.screen.ids.second_calc_btns
			if self.seconds_switched:
				for i,j in zip(*a):
					b.remove_widget(j)
					b.add_widget(i)
				self.screen.ids.swch_btn.text = "2nd"
				self.seconds_switched = False
			else:
				for i,j in zip(*a):
					b.remove_widget(i)
					b.add_widget(j)
				self.screen.ids.swch_btn.text = "1st"
				self.seconds_switched = True
	# change angle mode
	def switch_angle(self):
			if self.angle_mode=='deg':
				self.evaler = NP('rad')
				self.angle_mode = 'rad'
				self.screen.ids.ang_btn.text = 'rad'
			elif self.angle_mode=='rad':
				self.evaler = NP('deg')
				self.angle_mode = 'deg'
				self.screen.ids.ang_btn.text = 'deg'
			
	# initializing the class
	def __init__(self, **kwargs):
		self.words = {
			"shqip":["Mosha","Sipërfaqja","BMI","Të dhëna","Data","Zbritje","Gjatësia","Masa","Sistemi\nNumerik","Shpejtësia","Temperatura","Koha","Volumi","Monedha","Investimi","Kredi","Cilësimet","Rreth","Dil","Të dal tani ?","ANULLO","PO","Binar","Oktal","Decimal","Heksadecimal"],
			"english":["Age","Area","BMI","Data","Date","Discount","Length","Mass","Numeral\nSystem","Speed","Temperature","Time","Volume","Currency","Investment","Loan","Settings","About","Quit","Quit now ?","CANCEL","OK","Binary","Octal","Decimal","Hexadecimal"]
		}
		self.cwords = self.words["shqip"]
		# setting up parent class (is needed)
		super().__init__(**kwargs)
		# default theme (the only point responsible for theming)
		self.colors = self.decide_colors("Dark")
		# loading the file responsible for the hierarchy of widgets
		self.screen = Builder.load_file("main.kv")
		# check the main buttons layout
		self.main_switched = False
		# check the secondary buttons
		self.seconds_switched = False
		# creating instances for the layers in `main_scr`
		self.mcl = self.screen.ids.main_calc_btns
		self.scl = self.screen.ids.second_calc_btns
		# also instances for secondary buttons
		self.sin = self.screen.ids.sin_btn
		self.cos = self.screen.ids.cos_btn
		self.tan = self.screen.ids.tan_btn
		self.asin = self.screen.ids.asin_btn
		self.acos = self.screen.ids.acos_btn
		self.atan = self.screen.ids.atan_btn
		# removing temporarily buttons and a layer
		self.screen.ids.main_scr.remove_widget(self.scl)
		self.screen.ids.second_calc_btns.remove_widget(self.asin)
		self.screen.ids.second_calc_btns.remove_widget(self.acos)
		self.screen.ids.second_calc_btns.remove_widget(self.atan)
		# calculator's angle mode
		self.angle_mode = 'deg'
		# evaluater instance
		self.evaler = NP(self.angle_mode)
		# two theme's settings used as default
		self.theme_cls.theme_style = self.colors[0]
		self.theme_cls.primary_palette = self.colors[1]
		# loading conversion coefficients
		with open('conversions.json','r') as f:
			self.convs = load(f)
		self.exit_dialog = None
		# default screen (changable)
		self.curr_main = "main_scr"
		self.exit_menu = self.make_dropdown(
			[self.cwords[16],self.cwords[17],self.cwords[18]],
			[
				lambda x="Settings":self.menu_callback(x),
				lambda x="About":self.menu_callback(x),
				lambda x="Quit":self.menu_callback(x)
			],
			self.screen.ids.menu_caller)

	# this is needed (builds up the whole program)
	def build(self):
		return self.screen
	# method to response `exit_menu` events
	def menu_callback(self,call):
		if call=="Settings":
			self.root.ids.my_toolbar.opacity = 0
			self.root.ids.my_toolbar.disabled = True
			self.change_screen("settings_scr")
		if call=="About":
			self.root.ids.my_toolbar.opacity = 0
			self.root.ids.my_toolbar.disabled = True
			self.change_screen("about_scr")
		if call=="Quit":
			self.dialog()
		self.exit_menu.dismiss()
	# method to change screens (prime ones)
	# also applying effects
	def change_screen(self,screen):
		color = self.colors[4]
		current = self.root.ids.manager.current
		if screen == "main_scr":
			self.root.ids.main_btn.icon_color = self.theme_cls.primary_color
			self.root.ids.conv_btn.icon_color = color
			self.root.ids.curr_btn.icon_color = color
			if current=="about_scr":
				self.root.ids.my_toolbar.opacity = 1
				self.root.ids.my_toolbar.disabled = False
			if current=="settings_scr":
				self.root.ids.my_toolbar.opacity = 1
				self.root.ids.my_toolbar.disabled = False
		elif screen == "converter_scr":
			self.root.ids.main_btn.icon_color = color
			self.root.ids.conv_btn.icon_color = self.theme_cls.primary_color
			self.root.ids.curr_btn.icon_color = color
		elif screen == "currency_scr":
			self.root.ids.main_btn.icon_color = color
			self.root.ids.conv_btn.icon_color = color
			self.root.ids.curr_btn.icon_color = self.theme_cls.primary_color
		self.root.ids.manager.current = screen
	# this also changes screens, but is used only for converters
	# TODO: add statements to change on unpure conversions
	def change_screen1(self,t,r):
		if t=="bases":
			self.root.ids.manager.current = "bases-convy"
			self.screen.ids.bases_first.text = "dec"
			self.screen.ids.bases_second.text = "dec"
			self.bases_first_menu = self.make_dropdown(
			["Binar","Oktal","Decimal","Hexadecimal"],
			[lambda x=i:self.change_label(x,1)for i in ["bin","oct","dec","hex"]],
			self.screen.ids.bases_first
		)
			self.bases_second_menu = self.make_dropdown(
			["Binar","Oktal","Decimal","Hexadecimal"],
			[lambda x=i:self.change_label(x,0)for i in ["bin","oct","dec","hex"]],
			self.screen.ids.bases_second
		)
		else:
			self.init_convers(t,r)
			self.root.ids.manager.current = "convy"
	# this shows a toast
	# TODO: fond a use for it
	def show_toast(self,text):
		toast(text)
	# inserting values from buttons to input labels
	def insert_value(self,val):
		d = self.screen.ids.manager.current
		if d=="main_scr":
			c = self.root.ids.the_input.text
			if c=='0' and val!='.':
				self.root.ids.the_input.text = val
			else:
				z = ([1,0][len(i)>2]for i in (i.split('.')for i in re.split('[^0-9.-]',c)))
				if not all(z):
					return
				self.root.ids.the_input.text = c+val
		elif d=="convy":
			c = self.root.ids.input_label.text
			if c=='0' and val!='.':
				self.root.ids.input_label.text = val
			else:
				z = ([1,0][len(i)>2]for i in (i.split('.')for i in re.split('[^0-9.-]',c)))
				if not all(z):
					return
				self.root.ids.input_label.text = c+val
		elif d=="bases-convy":
			c = self.root.ids.bases_input_label.text
			if c == "0":
				self.root.ids.bases_input_label.text = val
			else:
				self.root.ids.bases_input_label.text = c+val
	# the `C` button functionality
	def clear_input(self):
		c = self.root.ids.manager.current
		if c == "main_scr":
			self.root.ids.the_input.text = "0"
		elif c == "convy":
			self.root.ids.input_label.text = "0"
			self.root.ids.output_label.text = "0"
		elif c == "bases-convy":
			self.root.ids.bases_input_label.text = "0"
			self.root.ids.bases_output_label.text = "0"
	# this pops one char from inputs
	def backspace(self):
		c = self.root.ids.manager.current
		if c == "main_scr":
			d = self.root.ids.the_input.text
			self.root.ids.the_input.text = d[:-1] if len(d)>1 else "0"
		elif c == "convy":
			d = self.root.ids.input_label.text
			self.root.ids.input_label.text = d[:-1] if len(d)>1 else "0"
		elif c == "bases-convy":
			d = self.root.ids.bases_input_label.text
			self.root.ids.bases_input_label.text = d[:-1] if len(d)>1 else "0"

	# here I am using `eval` because there cannot be vulnerabilities using numbers only
	# P.S. I may be wrong
	def evaluate(self):
		c = self.root.ids.the_input.text
		try:
			r = self.evaler.eval(c)
			if float(r)==int(r):
				r=int(r)
			else:
				r=round(r,15)
			self.root.ids.the_input.text = f'{r:,}'[:15]
		except Exception as e:
	# TODO: Maybe you can do something here
			print(e)
	# this is the `exit_dialog` formation
	def dialog(self):
		def dfunc(n):
			if n:
				exit()
			else:
				self.exit_dialog.dismiss(force=True)
			self.exit_dialog = None
		if not self.exit_dialog:
			self.exit_dialog = MDDialog(text=self.cwords[19],buttons=[MDFlatButton(text=self.cwords[20],theme_text_color="Custom",text_color=self.theme_cls.primary_color,on_release=lambda x:dfunc(0)),MDFlatButton(text=self.cwords[21],theme_text_color="Custom",text_color=self.theme_cls.primary_color,on_release=lambda x:dfunc(1))],radius=[20,20,20,20])
			self.exit_dialog.open()
	# converting pure units (convert screen only)
	def convert(self):
		fromUnit = self.screen.ids.first.text
		toUnit = self.screen.ids.second.text
		f = self.current[fromUnit]
		t = self.current[toUnit]
		# here I do two operations without considering the types of units
		# so they can be the same, one-way or impossibe conversions
		r = (float(self.screen.ids.input_label.text)/f)*t
		if float(r)==int(r):
			r=int(r)
		self.screen.ids.output_label.text = str(r)
	
	# this is used to convert a number from given base to another
	def conv_bases(self):
		n = self.screen.ids.bases_input_label.text
		f = self.screen.ids.bases_first.text
		t = self.screen.ids.bases_second.text
		a={"bin":2,"oct":8,"dec":10,"hex":16}.get(f,10)
		b={"bin":bin,"oct":oct,"dec":int,"hex":hex}.get(t,int)
		try:
			to_dec = int(n,a)
			to_other = str((lambda x:x(to_dec))(b))
		except Exception as e:
			self.show_toast(e)
			return
		if any(to_other.count(i)for i in'box'):
			to_other = to_other[2:]
		self.screen.ids.bases_output_label.text = to_other
	# used to adapt menus' texts upon unit choosing
	def change_label(self,unit,w):
		if self.root.ids.manager.current!="bases-convy":
			if w:
				self.screen.ids.first.text = unit
				self.first_menu.dismiss()
			else:
				self.screen.ids.second.text = unit
				self.second_menu.dismiss()
		else:
			if w:
				self.screen.ids.bases_first.text = unit
				self.bases_first_menu.dismiss()
			else:
				self.screen.ids.bases_second.text = unit
				self.bases_second_menu.dismiss()		

if __name__ in ["__main__","__android__"]:
	MainBaseApp().run()