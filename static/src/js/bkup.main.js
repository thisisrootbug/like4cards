odoo.define('like4cards.like4cards_screen', function(require) {
	"use strict";
	var screens = require('point_of_sale.screens');
	var reprint_screen = require('pos_order_reprint.pos_order_reprint');
	var session = require('web.session');	
	var PosBaseWidget = require('point_of_sale.BaseWidget');	
	var chrome = require('point_of_sale.chrome');
	var models = require('point_of_sale.models');

	screens.ProductCategoriesWidget.include({
		set_category : function(category){
			self = this;

            if(!category){
				 return this._super();
			}
			if(category.id > 10000){
                var products = [];
                session.rpc("/like4cards/get_products",{categoryId: category.id / 10000 }).then(function(data){
                    var jdata = JSON.parse(data);
                    if(jdata.response == 1 ){
                    var products = [];
                    jdata.data.forEach(product => { 
						var id = parseInt(product["productId"]) * 10000;
						var product_template = {
							"cid": "c"+category.id,
							"attributes": {},
							"_changing": false,
							"_previousAttributes": {},
							"changed": {},
							"_pending": false,
							"id": id,
							"barcode": "",
							"default_code": false,
							"product_tmpl_id": 5,
							"arabic_name": false,
							"sh_arabic_name": "",
							"list_price": parseFloat(product["productPrice"]),
							"categ_id": [
								category.id,
								category.name
							],
							"pos_categ_id": false,
							"taxes_id": [],
							"to_weight": false,
							"uom_id": [
								1,
								"Unit(s)"
							],
							"description_sale": false,
							"description": false,
							"tracking": "none",
							"not_returnable": false,
							"type": "product",
							"addon_ids": [],
							"has_addons": false,
							"has_multi_uom": false,
							"multi_uom_ids": [],
							"loyalty_point": 0,
							"display_name": product["productName"],
							"lst_price": parseFloat(product["productPrice"]),
							"standard_price": parseFloat(product["productPrice"]),
							"categ": {
								"id": category.id,
								"name": category.name,
								"parent_id": category.parent_id
							},
                            "get_price": function(price,quantity){ return parseFloat(product["productPrice"]);  },
                            "image_url": product["productImage"],
                            "is_like4cards_product": true,
						}
                        products.push(product_template);

                    });
                        self.pos.db.add_products(products);
                        self.product_list_widget.set_product_list(products); 
                    }else{
                        self.gui.show_popup('confirm',{
                            'title': 'Like4cards',
                            'body': jdata.message,
                            confirm: function(){
                                self.set_category(self.pos.db.root_category_id);
                            }
                        });
                    }
                },function(err,ev){
                    ev.preventDefault();
                    var error_body = 'Your Internet connection is probably down.';
                    if (err.data) {
                        var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': 'Error: Could not Load Categories',
                        'body': error_body,
                    });
                });
            }
			if(category.name == "Like4Cards"){
                session.rpc("/like4cards/get_categories",{}).then(function(data){
                    var jdata = JSON.parse(data);
                    var cats = [];
                    jdata.data.forEach(cat => { 
                            cat["id"] = 10000 * parseInt(cat["id"]);
                            cat["categoryParentId"] = parseInt(cat["categoryParentId"]);
                            cat["parent_id"] = category.id;
                            cat["name"] = cat.categoryName;
                            cat["image_url"] = cat.amazonImage;
                            cats.push(cat);
                    });
                    self.pos.db.add_categories(cats);
                    self.set_category(self.pos.db.root_category_id);
                    self.renderElement();
                },function(err,ev){
                    ev.preventDefault();
                    var error_body = 'Your Internet connection is probably down.';
                    if (err.data) {
                        var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': 'Error: Could not Load Categories',
                    'body': error_body,
                });
						});
				self.renderElement();
				return;
			}else{
				 return this._super(category);
			}
		},
        get_image_url: function(category){
            self = this;
            if(!category.image_url){
                return this._super(category);
            }
            return category.image_url;
        },


	});

	screens.ProductListWidget.include({
        get_product_image_url: function(product){
            self = this;
            if(!product.image_url){
                return this._super(product);
            }
            return product.image_url;
        },
	});

	screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            self = this;
            var order = this.pos.get_order();
            var get_data = async function(line){
                if(line.product.is_like4cards_product){
                        var productId = line.product.id / 10000;
                        //TODO change for production
                        productId = 376; // this is a test product
                        var response = await session.rpc("/like4cards/create_order", {
                            productId: productId,
                            referenceId: order.name+"-"+1
                        }).then(function(data){
                            var jdata = JSON.parse(data);
                            if(jdata.response == 1){
                                line["line_note"] += "<br/>serialCode:  "+jdata.serials[0].serialCode;
                            }
                        },function(err,ev){
                            ev.preventDefault();
                            var error_body = 'Your Internet connection is probably down.';
                            if (err.data) {
                                var except = err.data;
                                error_body = except.arguments && except.arguments[0] || except.message || error_body;
                            }
                            self.gui.show_popup('error',{
                                'title': 'Error: Could not Load Categories',
                                'body': error_body,
                            });
                        });
                    }
            }
            if (self.order_is_valid(force_validation)) {
                var this_super = this._super;
                var orderlines = order.get_orderlines();
                 for(var line of orderlines){
                     get_data(line);
                }
                return self.finalize_validation();
            }
        }
    });

	reprint_screen.include({
        get_receipt_render_env: function (results,myself) {
            var res = this._super(results,myself );
            self = this;
            res.receipt.orderlines.forEach(line => {
                if(line.product_name == "Like4Cards Products"){
                    return session.rpc("/like4cards/order_details", {
                            referenceId: res.receipt.pos_ref+"-"+1
                        }).then(function(data){
                            var jdata = JSON.parse(data);
                            if(jdata.response == 1){
                                line["line_note"] = jdata.serials[0].productName + `
                                serialCode: `+jdata.serials[0].serialCode;
                            }
                            if(!res.dont_recuse){
                                res["dont_recuse"] = true;
                                self.gui.show_screen("reprint_ticket");
                                self.chrome.screens.reprint_ticket.render_receipt(res,self);
                            }
                            return res;
                        },function(err,ev){
                            ev.preventDefault();
                            var error_body = 'Your Internet connection is probably down.';
                            if (err.data) {
                                var except = err.data;
                                error_body = except.arguments && except.arguments[0] || except.message || error_body;
                            }
                            self.gui.show_popup('error',{
                                'title': 'Error: Could not Load Categories',
                                'body': error_body,
                            });
                        });
                }
                
            });
        }
     });

	var Like4cardsStatusWidget = PosBaseWidget.extend({
		template: 'Like4cardsStatusWidget',
		
		init: function(parent, options) {
			this._super(parent, options);
		},

		start: function(){
			var self = this;
			self._super();
			this.$el.on("click",function(event){
                var like4cards_category = {"id": 1,"name": "Like4Cards","parent_id": 0};
                self.pos.categories.forEach(cat => {
                    if(cat.name == "Like4Cards"){
                        try{ self.pos.chrome.screens.products.product_categories_widget.set_category(cat); }catch(err){ console.error(err); }
                    }
                });
			});
			

		}
	});
	chrome.Chrome.prototype.widgets.unshift({
		'name':   'like4cards_status',
		'widget': Like4cardsStatusWidget,
		'append':  '.pos-rightheader',
	});


	/*models.OrderLine.include({
        init_from_JSON: function(json) {
            this.product = this.pos.db.get_product_by_id(json.product_id);
            if (!this.product) {
                console.error('Like4Cards ERROR: attempting to recover product ID', json.product_id,
                    'not available in the point of sale. Correct the product or clean the browser cache.');
                return;
            }
            return this._super(json);
        },

    }); */
	
});
