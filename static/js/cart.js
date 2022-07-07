
var updateBtns = document.getElementsByClassName('update-cart')


    for(var i = 0; i < updateBtns.length; i++){
      updateBtns[i].addEventListener('click',function(){
        var productID = this.dataset.product
        var action = this.dataset.action
        console.log('productID:',productID,'action:',action)

        console.log('USER:',user)
        if(user == 'AnonymousUser'){
          addCookieItem()
        }else{
          updateUserOrder(productID, action)
        }
      })
    }
    
    function addCookieItem(productID, action){
        console.log('Not Logged in...')
    }
    
    function updateUserOrder(productID, action){
      console.log('User is logged in, sending data...')
      
      var url = '/update_item/'
      const request = new Request(
        url,
        {headers: {'Content-Type':'application/json','X-CSRFToken': csrftoken}}
      );
      fetch(request, {
        method:'POST',
        body:JSON.stringify({'productID':productID,'action':action})
      })

      .then((response) =>{
        return response.json()
      })
      
      .then((data) =>{
        console.log('data:',data)
        location.reload()
      })
    }