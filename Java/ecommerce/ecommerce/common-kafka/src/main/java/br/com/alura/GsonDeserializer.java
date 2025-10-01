package br.com.alura;

import java.nio.charset.StandardCharsets;
import java.util.Map;

import org.apache.kafka.common.serialization.Deserializer;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class GsonDeserializer<T> implements Deserializer<T> {

    public static final String TYPE_CONFIG = "br.com.alura.ecommerce.type_config";
    private final Gson gson = new GsonBuilder().create();
    private Class<T> type;

    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
       Object typeConfig = configs.get(TYPE_CONFIG);
       if(typeConfig == null){
           throw new IllegalStateException("Type for deserialization was not configured.");
       }
       String typeName = typeConfig.toString();
       try {
         this.type = (Class<T>) Class.forName(typeName);
    } catch (ClassNotFoundException e) {
        // TODO Auto-generated catch block
        throw new RuntimeException("Type for deserialization does not exist in the classpath.",e);
    }
    }


    @Override
    public T deserialize(String s, byte[] bytes) {
        if(bytes == null){
            return null;
        }
        return gson.fromJson(new String(bytes, StandardCharsets.UTF_8), type);
    }


}
