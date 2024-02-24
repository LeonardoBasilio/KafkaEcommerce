package br.com.alura;

import java.math.BigDecimal;
import java.util.UUID;
import java.util.concurrent.ExecutionException;

public class NewOrderMain {
    public static void main(String[] args) throws InterruptedException, ExecutionException {
        try (var orderDispatcher = new KafkaDispatcher<Order>()) {
            try (var emailDispatcher = new KafkaDispatcher<String>()) {

                for (var i = 0; i < 10; i++) {
                    //System.out.println("Hello world!");
                    var userId  = UUID.randomUUID().toString();
                    var orderId = UUID.randomUUID().toString();
                    var amount  = new BigDecimal(Math.random() * 5000 + 1);
                    var order = new Order(userId, orderId, amount);
                    orderDispatcher.send("ECOMMERCE_NEW_ORDER",userId, order);

                    var email = "Thank you for your order! we are processing your order!";  
                    emailDispatcher.send("ECOMMERCE_SEND_EMAIL",userId, email);
                }
            }
        } 

    }
}